from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from core.exceptions import PolicyViolationError


@dataclass
class PolicyEngine:
    """
    Hard policy checks only.
    No "smart" logic: rules are explicit and deterministic.
    """

    rules: Dict[str, Any]

    def check(self, subject: str, ctx_view: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        violations: List[Dict[str, Any]] = []

        # Example hard rules:
        # - required permissions
        # - forbidden actions/tools
        # - role-based constraints
        subject_rules = self.rules.get(subject, {})
        required_perms = subject_rules.get("required_permissions", [])
        forbidden = subject_rules.get("forbidden", [])

        perms = set(ctx_view.get("permissions", []))
        for rp in required_perms:
            if rp not in perms:
                violations.append({
                    "type": "missing_permission",
                    "permission": rp,
                    "subject": subject,
                })

        action = ctx_view.get("action")
        if action and action in forbidden:
            violations.append({
                "type": "forbidden_action",
                "action": action,
                "subject": subject,
            })

        ok = len(violations) == 0
        return ok, violations

    def enforce(self, subject: str, ctx_view: Dict[str, Any]) -> None:
        ok, violations = self.check(subject, ctx_view)
        if not ok:
            raise PolicyViolationError(f"Policy violation on '{subject}': {violations}")
