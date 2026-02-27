from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from core.context import ExecutionContext
from core.decision import Decision, DecisionStatus
from governance.gates.base import GateBase


@dataclass
class Gate0AgentDefinition(GateBase):
    def __init__(self) -> None:
        super().__init__(gate_id="gate-0", name="Agent Definition & Boundaries", hard=True)

    def evaluate(self, ctx: ExecutionContext) -> Decision:
        # Hard checks: identity + boundaries existence
        missing = []
        if not ctx.actor_agent_id or ctx.actor_agent_id == "unknown-agent":
            missing.append("actor_agent_id")
        if not ctx.actor_role or ctx.actor_role == "unknown-role":
            missing.append("actor_role")
        if not isinstance(ctx.budget_caps, dict) or not ctx.budget_caps:
            missing.append("budget_caps")

        if missing:
            return Decision(
                status=DecisionStatus.DENY,
                reason="Missing required agent identity/boundaries fields",
                evidence={"missing": missing},
                alternatives=[{"action": "populate_required_fields", "missing": missing}],
                confidence=0.9,
            )

        return Decision(
            status=DecisionStatus.ALLOW,
            reason="Agent identity and boundaries present",
            evidence={"agent_id": ctx.actor_agent_id, "role": ctx.actor_role},
            confidence=0.85,
        )
