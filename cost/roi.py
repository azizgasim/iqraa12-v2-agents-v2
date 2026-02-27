from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ROIResult:
    value: float
    rationale: Dict[str, Any]


class ROIEngine:
    def compute(self, benefits: Dict[str, float], costs: Dict[str, float]) -> ROIResult:
        total_benefit = sum(benefits.values())
        total_cost = max(sum(costs.values()), 1e-6)
        return ROIResult(
            value=total_benefit / total_cost,
            rationale={"benefits": benefits, "costs": costs},
        )


class ROIEstimator:
    def estimate(self, outputs: Dict[str, Any], budget_used: Dict[str, float]) -> Dict[str, Any]:
        engine = ROIEngine()
        benefits = {"outputs": float(len(outputs))}
        costs = {"usd": budget_used.get("usd", 0.0)}
        return engine.compute(benefits, costs).__dict__
