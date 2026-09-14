from app.models.enums import MissionStatus, TaskStatus
from app.core.exceptions import ERRORS


MISSION_TRANSITIONS: dict[MissionStatus, set[MissionStatus]] = {
    MissionStatus.DRAFT: {MissionStatus.VALIDATING, MissionStatus.CANCELLED},
    MissionStatus.VALIDATING: {MissionStatus.PLANNED, MissionStatus.BLOCKED, MissionStatus.FAILED},
    MissionStatus.PLANNED: {MissionStatus.WAITING_FOR_APPROVAL, MissionStatus.APPROVED, MissionStatus.BLOCKED},
    MissionStatus.WAITING_FOR_APPROVAL: {MissionStatus.APPROVED, MissionStatus.BLOCKED, MissionStatus.EXPIRED},
    MissionStatus.APPROVED: {MissionStatus.RUNNING, MissionStatus.CANCELLED},
    MissionStatus.RUNNING: {MissionStatus.PAUSED, MissionStatus.CANCELLING, MissionStatus.COMPLETED, MissionStatus.FAILED},
    MissionStatus.PAUSED: {MissionStatus.RUNNING, MissionStatus.CANCELLING},
    MissionStatus.CANCELLING: {MissionStatus.CANCELLED, MissionStatus.FAILED},
    MissionStatus.CANCELLED: set(), MissionStatus.COMPLETED: set(), MissionStatus.FAILED: set(),
    MissionStatus.BLOCKED: set(), MissionStatus.EXPIRED: set(),
}


TASK_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.CREATED: {TaskStatus.READY, TaskStatus.BLOCKED, TaskStatus.CANCELLED},
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