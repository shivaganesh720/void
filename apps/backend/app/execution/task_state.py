from app.models.enums import MissionStatus, TaskStatus
from app.core.exceptions import ERRORS


MISSION_TRANSITIONS: dict[MissionStatus, set[MissionStatus]] = {
    MissionStatus.REQUESTED: {MissionStatus.VALIDATING, MissionStatus.CANCELLED},
    MissionStatus.DRAFT: {MissionStatus.VALIDATING, MissionStatus.CANCELLED},
    MissionStatus.VALIDATING: {MissionStatus.PLANNED, MissionStatus.WAITING_FOR_INPUT, MissionStatus.BLOCKED, MissionStatus.FAILED},
    MissionStatus.PLANNED: {MissionStatus.WAITING_FOR_INPUT, MissionStatus.WAITING_FOR_APPROVAL, MissionStatus.READY, MissionStatus.APPROVED, MissionStatus.BLOCKED, MissionStatus.REQUIRES_REVIEW},
    MissionStatus.WAITING_FOR_INPUT: {MissionStatus.VALIDATING, MissionStatus.CANCELLED, MissionStatus.BLOCKED},
    MissionStatus.WAITING_FOR_APPROVAL: {MissionStatus.APPROVED, MissionStatus.BLOCKED, MissionStatus.EXPIRED, MissionStatus.CANCELLED},
    MissionStatus.READY: {MissionStatus.RUNNING, MissionStatus.CANCELLED, MissionStatus.WAITING_FOR_APPROVAL},
    MissionStatus.APPROVED: {MissionStatus.RUNNING, MissionStatus.CANCELLED},
    MissionStatus.RUNNING: {MissionStatus.PAUSED, MissionStatus.CANCELLING, MissionStatus.COMPLETED, MissionStatus.PARTIALLY_COMPLETED, MissionStatus.FAILED, MissionStatus.TIMED_OUT, MissionStatus.REQUIRES_REVIEW},
    MissionStatus.PAUSED: {MissionStatus.RUNNING, MissionStatus.CANCELLING, MissionStatus.CANCELLED},
    MissionStatus.CANCELLING: {MissionStatus.CANCELLED, MissionStatus.FAILED},
    MissionStatus.CANCELLED: set(), MissionStatus.COMPLETED: set(), MissionStatus.PARTIALLY_COMPLETED: set(), MissionStatus.FAILED: set(),
    MissionStatus.BLOCKED: set(), MissionStatus.EXPIRED: set(), MissionStatus.TIMED_OUT: set(), MissionStatus.REQUIRES_REVIEW: set(),
}


TASK_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.CREATED: {TaskStatus.READY, TaskStatus.WAITING, TaskStatus.BLOCKED, TaskStatus.CANCELLED},
    TaskStatus.READY: {TaskStatus.QUEUED, TaskStatus.BLOCKED, TaskStatus.CANCELLED},
    TaskStatus.QUEUED: {TaskStatus.RUNNING, TaskStatus.CANCELLED, TaskStatus.TIMED_OUT},
    TaskStatus.RUNNING: {TaskStatus.SUCCEEDED, TaskStatus.FAILED, TaskStatus.RETRYING, TaskStatus.CANCELLED, TaskStatus.TIMED_OUT},
    TaskStatus.RETRYING: {TaskStatus.QUEUED, TaskStatus.FAILED, TaskStatus.CANCELLED},
    TaskStatus.WAITING: {TaskStatus.READY, TaskStatus.CANCELLED, TaskStatus.TIMED_OUT},
    TaskStatus.SUCCEEDED: set(), TaskStatus.FAILED: set(), TaskStatus.CANCELLED: set(), TaskStatus.BLOCKED: set(), TaskStatus.TIMED_OUT: set(),
}


def validate_transition(current: MissionStatus | TaskStatus, target: MissionStatus | TaskStatus) -> None:
    transitions = MISSION_TRANSITIONS if isinstance(current, MissionStatus) else TASK_TRANSITIONS
    if target not in transitions[current]:
        raise ValueError(ERRORS["INVALID_STATE_TRANSITION"].code)
