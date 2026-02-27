from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .lifecycle import LifecycleState


@dataclass
class ExecutionContext:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    # Identity / role / permissions
    actor_agent_id: str = "unknown-agent"
    actor_role: str = "unknown-role"
    permissions: List[str] = field(default_factory=list)

    # Budget
    budget_caps: Dict[str, float] = field(default_factory=lambda: {
        "tokens": 50_000.0,
        "tool_calls": 50.0,
        "wall_ms": 120_000.0,
        "usd": 5.0,
    })
    budget_used: Dict[str, float] = field(default_factory=lambda: {
        "tokens": 0.0,
        "tool_calls": 0.0,
        "wall_ms": 0.0,
        "usd": 0.0,
    })

    # Policies / Modes
    mode: str = "standard"  # lean | standard | rigorous | jury
    policies: Dict[str, Any] = field(default_factory=dict)

    # Inputs/Outputs
    request: Dict[str, Any] = field(default_factory=dict)
    plan: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)

    # Governance traces
    gate_decisions: List[Dict[str, Any]] = field(default_factory=list)
    audit_events: List[Dict[str, Any]] = field(default_factory=list)

    # Lifecycle
    lifecycle: LifecycleState = field(default_factory=LifecycleState)

    # Safety / stop flags
    stop_now: bool = False
    stop_reason: Optional[str] = None
