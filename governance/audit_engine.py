from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict

from core.context import ExecutionContext


@dataclass
class AuditEngine:
    enabled: bool = True

    def emit(self, ctx: ExecutionContext, event_type: str, payload: Dict[str, Any], *, severity: str = "info") -> Dict[str, Any]:
        if not self.enabled:
            return {}

        evt = {
            "event_id": str(uuid.uuid4()),
            "ts_ms": int(time.time() * 1000),
            "session_id": ctx.session_id,
            "task_id": ctx.task_id,
            "agent_id": ctx.actor_agent_id,
            "role": ctx.actor_role,
            "event_type": event_type,
            "severity": severity,
            "payload": payload,
        }
        ctx.audit_events.append(evt)
        return evt

    def dumps(self, ctx: ExecutionContext) -> str:
        return json.dumps(ctx.audit_events, ensure_ascii=False, indent=2)
