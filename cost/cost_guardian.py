from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class CostDecision:
    allowed: bool
    estimated_usd: float
    cap_usd: float


class CostGuardian:
    def preflight(self, estimate_usd: float, cap_usd: float) -> CostDecision:
        return CostDecision(
            allowed=estimate_usd <= cap_usd,
            estimated_usd=estimate_usd,
            cap_usd=cap_usd,
        )

    def assess(self, plan: Dict[str, Any], caps: Dict[str, float], used: Dict[str, float]) -> CostDecision:
        cap_usd = caps.get("usd", 0.0)
        est = plan.get("estimated_usd", used.get("usd", 0.0))
        return self.preflight(est, cap_usd)

    def assess_plan(self, plan: Dict[str, Any]) -> CostDecision:
        est = plan.get("estimated_usd", 0.0)
        cap = plan.get("cap_usd", est)
        return self.preflight(est, cap)
