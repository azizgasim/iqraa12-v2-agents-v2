from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class DecisionStatus(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    DEFER = "defer"
    SOFT_DENY = "soft_deny"


@dataclass
class Decision:
    status: DecisionStatus
    reason: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.75

    @property
    def ok(self) -> bool:
        return self.status == DecisionStatus.ALLOW
