from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from core.context import ExecutionContext
from core.decision import Decision, DecisionStatus
from governance.gates.base import GateBase


@dataclass
class Gate4QualityEval(GateBase):
    def __init__(self) -> None:
        super().__init__(gate_id="gate-4", name="Quality/Evals/Regression Gate", hard=False)

    def evaluate(self, ctx: ExecutionContext) -> Decision:
        # Soft gate: require quality checklist presence
        plan = ctx.plan or {}
        checklist = plan.get("quality_checklist", [])
        if not isinstance(checklist, list) or len(checklist) == 0:
            return Decision(
                status=DecisionStatus.SOFT_DENY,
                reason="Missing quality_checklist (soft requirement)",
                evidence={},
                alternatives=[{"action": "add_quality_checklist", "examples": ["coherence", "traceability", "policy_ok"]}],
                confidence=0.7,
            )
        return Decision(
            status=DecisionStatus.ALLOW,
            reason="Quality checklist present",
            evidence={"items": len(checklist)},
            confidence=0.75,
        )
