from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class LifecyclePhase(str, Enum):
    INIT = "init"
    PLAN = "plan"
    GOVERN = "govern"
    EXECUTE = "execute"
    REVIEW = "review"
    FINALIZE = "finalize"
    FAILED = "failed"


@dataclass
class LifecycleState:
    phase: LifecyclePhase = LifecyclePhase.INIT
    last_error: Optional[str] = None
