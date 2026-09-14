from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorDefinition:
    code: str
    status_code: int
    message: str
    retryable: bool = False


ERRORS = {
    "PROJECT_NOT_FOUND": ErrorDefinition("PROJECT_NOT_FOUND", 404, "The project was not found."),
    "INVALID_STATE_TRANSITION": ErrorDefinition("INVALID_STATE_TRANSITION", 409, "The requested state transition is not allowed."),
    "POLICY_BLOCKED": ErrorDefinition("POLICY_BLOCKED", 403, "Policy blocked this action."),
    "INTERNAL_ERROR": ErrorDefinition("INTERNAL_ERROR", 500, "An internal error occurred.", True),
}