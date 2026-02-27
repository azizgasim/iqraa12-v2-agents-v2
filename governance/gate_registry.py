from __future__ import annotations

from dataclasses import dataclass
from typing import List

from governance.gates.base import GateBase
from governance.gates.gate0_agent_definition import Gate0AgentDefinition
from governance.gates.gate1_organization import Gate1Organization
from governance.gates.gate2_values_incentives import Gate2ValuesIncentives
from governance.gates.gate3_safety_shutdown import Gate3SafetyShutdown
from governance.gates.gate4_quality_eval import Gate4QualityEval
from governance.gates.gate5_budget_cost import Gate5BudgetCost


@dataclass
class GateRegistry:
    def build_default(self) -> List[GateBase]:
        return [
            Gate0AgentDefinition(),
            Gate1Organization(),
            Gate2ValuesIncentives(),
            Gate3SafetyShutdown(),
            Gate4QualityEval(),
            Gate5BudgetCost(),
        ]
