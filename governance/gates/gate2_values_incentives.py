from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from core.context import ExecutionContext
from core.decision import Decision, DecisionStatus
from governance.gates.base import GateBase


@dataclass
class Gate2ValuesIncentives(GateBase):
    def __init__(self) -> None:
        super().__init__(gate_id="gate-2", name="Values/Incentives/Anti-Gaming", hard=True)

    def evaluate(self, ctx: ExecutionContext) -> Decision:
        # Minimal wiring: require explicit intent + alternatives in plan header
        plan = ctx.plan or {}
        intent = plan.get("intent")
        alternatives = plan.get("alternatives", [])
        if not intent:
            return Decision(
                status=DecisionStatus.DENY,
                reason="Missing intent in plan (Intentionality required)",
                evidence={"plan_keys": list(plan.keys())},
                alternatives=[{"action": "set_plan_intent"}],
                confidence=0.9,
            )
        if not isinstance(alternatives, list) or len(alternatives) < 2:
            return Decision(
                status=DecisionStatus.DENY,
                reason="Missing alternatives in plan (Alternatives required)",
                evidence={"alternatives_count": len(alternatives) if isinstance(alternatives, list) else None},
                alternatives=[{"action": "add_plan_alternatives", "min": 2}],
                confidence=0.85,
            )

        return Decision(
            status=DecisionStatus.ALLOW,
            reason="Values constraints satisfied (intent + alternatives present)",
            evidence={"intent": intent, "alternatives_count": len(alternatives)},
            confidence=0.8,
        )
