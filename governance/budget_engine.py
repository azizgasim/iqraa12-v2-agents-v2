from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Tuple

from core.context import ExecutionContext
from core.exceptions import BudgetExceededError


@dataclass
class BudgetEngine:
    hard_stop: bool = True

    def start_timer(self) -> float:
        return time.time()

    def stop_timer_and_charge(self, ctx: ExecutionContext, start_s: float) -> None:
        elapsed_ms = (time.time() - start_s) * 1000.0
        self.charge(ctx, {"wall_ms": elapsed_ms})

    def charge(self, ctx: ExecutionContext, usage: Dict[str, float]) -> Tuple[bool, Dict[str, Any]]:
        # Apply usage
        for k, v in usage.items():
            ctx.budget_used[k] = float(ctx.budget_used.get(k, 0.0)) + float(v)

        # Check caps
        over = {}
        for k, cap in ctx.budget_caps.items():
            used = ctx.budget_used.get(k, 0.0)
            if used > cap:
                over[k] = {"used": used, "cap": cap}

        ok = len(over) == 0
        detail = {"ok": ok, "over": over, "used": dict(ctx.budget_used), "caps": dict(ctx.budget_caps)}

        if (not ok) and self.hard_stop:
            raise BudgetExceededError(f"Budget exceeded: {over}")

        return ok, detail
