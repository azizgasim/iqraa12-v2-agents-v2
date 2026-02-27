from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from core.context import ExecutionContext
from core.decision import Decision, DecisionStatus
from governance.gates.base import GateBase


@dataclass
class Gate3SafetyShutdown(GateBase):
    def __init__(self) -> None:
        super().__init__(gate_id="gate-3", name="Safety/Failure/Safe Shutdown", hard=True)

    def evaluate(self, ctx: ExecutionContext) -> Decision:
        # Hard check: must have stop mechanism / flags wired
        if ctx.stop_now:
            return Decision(
                status=DecisionStatus.DENY,
                reason="Context is flagged for stop_now",
                evidence={"stop_reason": ctx.stop_reason},
                alternatives=[{"action": "reset_stop_flag_if_safe", "requires": "human_approval"}],
                confidence=0.95,
            )

        # Require plan safety hooks
        plan = ctx.plan or {}
        if plan.get("on_violation") not in ("stop", "degrade", "defer"):
            return Decision(
                status=DecisionStatus.DENY,
                reason="Plan missing safety hook 'on_violation' (stop/degrade/defer)",
                evidence={"on_violation": plan.get("on_violation")},
                alternatives=[{"action": "set_on_violation", "allowed": ["stop", "degrade", "defer"]}],
                confidence=0.85,
            )

        return Decision(
            status=DecisionStatus.ALLOW,
            reason="Safety constraints satisfied",
            evidence={"on_violation": plan.get("on_violation")},
            confidence=0.8,
        )
