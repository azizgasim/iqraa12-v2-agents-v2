from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from core.context import ExecutionContext
from core.decision import Decision, DecisionStatus
from governance.gates.base import GateBase


@dataclass
class Gate1Organization(GateBase):
    def __init__(self) -> None:
        super().__init__(gate_id="gate-1", name="Multi-Agent Organization & Interaction", hard=True)

    def evaluate(self, ctx: ExecutionContext) -> Decision:
        # Enforce "no self-review": if a plan routes the same agent to review its own output => deny
        plan = ctx.plan or {}
        steps: List[Dict[str, Any]] = plan.get("steps", [])
        reviewer_ids = {s.get("agent_id") for s in steps if s.get("kind") == "review"}
        producer_ids = {s.get("agent_id") for s in steps if s.get("kind") in ("research", "analysis", "write", "execute")}

        overlap = sorted(list(reviewer_ids.intersection(producer_ids)))
        if overlap:
            return Decision(
                status=DecisionStatus.DENY,
                reason="Anti-pattern: agent reviewing its own work",
                evidence={"overlap_agent_ids": overlap},
                alternatives=[{"action": "assign_independent_reviewer", "suggest": "reviewer_agent_id != producer_agent_id"}],
                confidence=0.9,
            )

        return Decision(
            status=DecisionStatus.ALLOW,
            reason="Organization constraints satisfied",
            evidence={"steps": len(steps)},
            confidence=0.8,
        )
