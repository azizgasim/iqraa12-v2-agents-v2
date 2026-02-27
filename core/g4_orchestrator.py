from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from core.context import ExecutionContext
from core.decision import DecisionStatus
from core.exceptions import GateDeniedError, PolicyViolationError, BudgetExceededError, SafetyViolationError
from core.lifecycle import LifecyclePhase
from governance.audit_engine import AuditEngine
from governance.budget_engine import BudgetEngine
from governance.policy_engine import PolicyEngine
from governance.gates.base import GateBase
from execution.model_router import ModelRouter
from execution.tool_runner import ToolRunner
from execution.sandbox import Sandbox
from execution.job_manager import JobManager

from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.writing_agent import WritingAgent
from agents.reviewer_agent import ReviewerAgent
from core.creative_elite import CreativeNode

if TYPE_CHECKING:
    from eval.quality_engine import QualityEngine
    from eval.regression import RegressionSuite
    from cost.cost_guardian import CostGuardian
    from cost.roi import ROIEstimator
    from core.context_enrichment import ContextEnricher


@dataclass
class Orchestrator:
    gates: List[GateBase]
    policy_engine: PolicyEngine
    budget_engine: BudgetEngine
    audit_engine: AuditEngine

    model_router: ModelRouter
    tool_runner: ToolRunner
    sandbox: Sandbox
    job_manager: JobManager

    # Agents wired (IDs must be distinct to satisfy Gate-1)
    research_agent: ResearchAgent
    analysis_agent: AnalysisAgent
    writing_agent: WritingAgent
    reviewer_agent: ReviewerAgent

    creative_node: CreativeNode

    # Optional Phase Final controls
    quality_engine: "QualityEngine" | None = None
    regression_suite: "RegressionSuite" | None = None
    cost_guardian: "CostGuardian" | None = None
    roi_estimator: "ROIEstimator" | None = None
    context_enricher: "ContextEnricher" | None = None

    def _ctx_view(self, ctx: ExecutionContext, *, action: Optional[str] = None) -> Dict[str, Any]:
        return {
            "session_id": ctx.session_id,
            "task_id": ctx.task_id,
            "mode": ctx.mode,
            "permissions": list(ctx.permissions),
            "actor_agent_id": ctx.actor_agent_id,
            "actor_role": ctx.actor_role,
            "request": dict(ctx.request),
            "plan": dict(ctx.plan),
            "action": action,
            "budget_caps": dict(ctx.budget_caps),
            "budget_used": dict(ctx.budget_used),
        }

    def _run_gates(self, ctx: ExecutionContext) -> None:
        for g in self.gates:
            d = g.evaluate(ctx)
            g.record(ctx, d)

            self.audit_engine.emit(ctx, "gate_decision", {
                "gate_id": g.gate_id,
                "status": d.status.value,
                "reason": d.reason,
            })

            if d.status == DecisionStatus.DENY and g.hard:
                raise GateDeniedError(f"{g.gate_id} denied: {d.reason}")

            if d.status == DecisionStatus.SOFT_DENY and ctx.plan.get("on_violation") == "degrade":
                ctx.mode = "lean"

    def _enrich_context(self, ctx: ExecutionContext) -> None:
        if not self.context_enricher:
            return

        for layer in ctx.plan.get("context_layers", []):
            self.context_enricher.enrich(ctx, layer)
            has_context = bool(ctx.outputs.get("context", {}).get(layer))
            self.audit_engine.emit(ctx, "context_enriched", {"layer": layer, "present": has_context})

    def _cost_preflight(self, ctx: ExecutionContext) -> None:
        if not self.cost_guardian:
            return

        assessor = getattr(self.cost_guardian, "assess", None) or getattr(self.cost_guardian, "assess_plan", None)
        if assessor is None:
            return

        try:
            verdict = assessor(ctx.plan, ctx.budget_caps, ctx.budget_used)
        except TypeError:
            verdict = assessor(ctx.plan)

        allowed = bool(getattr(verdict, "allowed", verdict if verdict is not None else True))
        self.audit_engine.emit(ctx, "cost_preflight", {"allowed": allowed})
        if not allowed:
            raise BudgetExceededError("cost_guardian_preflight_blocked")

    def _post_review_checks(self, ctx: ExecutionContext) -> None:
        if self.quality_engine:
            quality = self.quality_engine.evaluate(ctx.outputs)
            payload = quality if isinstance(quality, dict) else {"ok": bool(quality)}
            self.audit_engine.emit(ctx, "quality_review", payload)

        if self.regression_suite:
            regression = self.regression_suite.run(ctx.outputs)
            payload = regression if isinstance(regression, dict) else {"ok": bool(regression)}
            self.audit_engine.emit(ctx, "regression_suite", payload)

        if self.roi_estimator:
            roi = self.roi_estimator.estimate(ctx.outputs, ctx.budget_used)
            payload = roi if isinstance(roi, dict) else {"value": roi}
            self.audit_engine.emit(ctx, "roi_estimate", payload)

    def _build_default_plan(self, ctx: ExecutionContext) -> None:
        ctx.plan = {
            "intent": ctx.request.get("intent", "fulfill_request_with_governance"),
            "alternatives": [
                {"path": "lean", "tradeoff": "lower_cost_lower_depth"},
                {"path": "standard", "tradeoff": "balanced"},
                {"path": "rigorous", "tradeoff": "higher_cost_higher_checking"},
            ],
            "on_violation": ctx.request.get("on_violation", "stop"),
            "quality_checklist": ["traceability", "policy_ok", "budget_ok"],
            "steps": [
                {"kind": "research", "agent_id": self.research_agent.agent_id},
                {"kind": "analysis", "agent_id": self.analysis_agent.agent_id},
                {"kind": "write", "agent_id": self.writing_agent.agent_id},
                {"kind": "review", "agent_id": self.reviewer_agent.agent_id},
            ],
        }

    def run(self, ctx: ExecutionContext) -> ExecutionContext:
        t0 = self.budget_engine.start_timer()
        try:
            ctx.lifecycle.phase = LifecyclePhase.INIT
            self.audit_engine.emit(ctx, "lifecycle", {"phase": ctx.lifecycle.phase.value})

            # PLAN
            ctx.lifecycle.phase = LifecyclePhase.PLAN
            self.audit_engine.emit(ctx, "lifecycle", {"phase": ctx.lifecycle.phase.value})
            if not ctx.plan:
                raise PolicyViolationError("plan_required")

            self._enrich_context(ctx)
            self._cost_preflight(ctx)

            # GOVERN: policy + gates + budget caps presence
            ctx.lifecycle.phase = LifecyclePhase.GOVERN
            self.audit_engine.emit(ctx, "lifecycle", {"phase": ctx.lifecycle.phase.value})

            self.policy_engine.enforce("orchestration", self._ctx_view(ctx, action="orchestrate"))
            self._run_gates(ctx)

            # EXECUTE: creative path or standard path
            ctx.lifecycle.phase = LifecyclePhase.EXECUTE
            self.audit_engine.emit(ctx, "lifecycle", {"phase": ctx.lifecycle.phase.value})

            if ctx.plan.get("intent") == "creative":
                problem = ctx.plan.get("creative_problem")
                if not problem:
                    raise PolicyViolationError("creative_problem_required")

                creative_out = self.creative_node.execute({"creative_problem": problem})
                ctx.outputs["creative_result"] = creative_out.get("creative_result")
                ctx.outputs["genesis_trace"] = creative_out.get("genesis_trace")
                self.audit_engine.emit(ctx, "creative_path", {
                    "result_present": bool(ctx.outputs.get("creative_result")),
                    "trace_len": len(ctx.outputs.get("genesis_trace", [])),
                })
            else:
                route = self.model_router.route(self._ctx_view(ctx))
                self.audit_engine.emit(ctx, "model_route", route)

                # Agents produce (stubs)
                research_out = self.research_agent.act(self._ctx_view(ctx, action="research"))
                analysis_out = self.analysis_agent.act(self._ctx_view(ctx, action="analysis"))
                writing_out = self.writing_agent.act(self._ctx_view(ctx, action="write"))

                ctx.outputs["research"] = research_out
                ctx.outputs["analysis"] = analysis_out
                ctx.outputs["draft"] = writing_out

                self.audit_engine.emit(ctx, "agent_outputs", {
                    "research": bool(research_out),
                    "analysis": bool(analysis_out),
                    "draft": bool(writing_out),
                })

                # REVIEW: independent reviewer
                ctx.lifecycle.phase = LifecyclePhase.REVIEW
                self.audit_engine.emit(ctx, "lifecycle", {"phase": ctx.lifecycle.phase.value})

                review_out = self.reviewer_agent.act(self._ctx_view(ctx, action="review"))
                ctx.outputs["review"] = review_out
                self.audit_engine.emit(ctx, "review_result", review_out)

                self._post_review_checks(ctx)

            # FINALIZE: budget charge (timer) + return
            ctx.lifecycle.phase = LifecyclePhase.FINALIZE
            self.audit_engine.emit(ctx, "lifecycle", {"phase": ctx.lifecycle.phase.value})

            return ctx

        except (GateDeniedError, PolicyViolationError, BudgetExceededError, SafetyViolationError) as e:
            ctx.lifecycle.phase = LifecyclePhase.FAILED
            ctx.lifecycle.last_error = str(e)
            ctx.stop_now = True
            ctx.stop_reason = str(e)
            self.audit_engine.emit(ctx, "failure", {"error": str(e)}, severity="error")
            return ctx

        finally:
            self.budget_engine.stop_timer_and_charge(ctx, t0)
            self.audit_engine.emit(ctx, "budget_snapshot", {
                "used": dict(ctx.budget_used),
                "caps": dict(ctx.budget_caps),
            })
