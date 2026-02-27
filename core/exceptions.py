class GateDeniedError(RuntimeError):
    pass


class BudgetExceededError(RuntimeError):
    pass


class PolicyViolationError(RuntimeError):
    pass


class SafetyViolationError(RuntimeError):
    pass
