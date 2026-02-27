from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from core.context import ExecutionContext
from core.decision import Decision


@dataclass
class GateBase:
    gate_id: str
    name: str
    hard: bool = True

    def evaluate(self, ctx: ExecutionContext) -> Decision:
        raise NotImplementedError

    def record(self, ctx: ExecutionContext, decision: Decision, *, meta: Optional[Dict[str, Any]] = None) -> None:
        ctx.gate_decisions.append({
            "gate_id": self.gate_id,
            "name": self.name,
            "hard": self.hard,
            "status": decision.status.value,
            "reason": decision.reason,
            "confidence": decision.confidence,
            "evidence": decision.evidence,
            "alternatives": decision.alternatives,
            "meta": meta or {},
        })
