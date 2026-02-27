from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from core.context import ExecutionContext
from core.decision import Decision, DecisionStatus
from governance.gates.base import GateBase


@dataclass
class Gate5BudgetCost(GateBase):
    def __init__(self) -> None:
        super().__init__(gate_id="gate-5", name="Budget/Cost Governance", hard=True)

    def evaluate(self, ctx: ExecutionContext) -> Decision:
        # Hard check: caps exist and are sane
        caps = ctx.budget_caps or {}
        required = ["tokens", "tool_calls", "wall_ms", "usd"]
        missing = [k for k in required if k not in caps]
        if missing:
            return Decision(
                status=DecisionStatus.DENY,
                reason="Missing required budget caps",
                evidence={"missing": missing, "caps": caps},
                alternatives=[{"action": "set_budget_caps", "required": required}],
                confidence=0.9,
            )
        return Decision(
            status=DecisionStatus.ALLOW,
            reason="Budget caps OK",
            evidence={"caps": caps},
            confidence=0.8,
        )
