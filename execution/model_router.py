from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ModelRouter:
    def route(self, ctx_view: Dict[str, Any]) -> Dict[str, Any]:
        # Deterministic placeholder routing by mode
        mode = ctx_view.get("mode", "standard")
        if mode == "lean":
            model = "small"
        elif mode == "rigorous":
            model = "large"
        elif mode == "jury":
            model = "large+verifier"
        else:
            model = "standard"
        return {"model": model}
