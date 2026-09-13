import pytest

from app.contracts.enums import MissionStatus, TaskStatus
from app.control_plane.state import validate_transition


def test_valid_mission_transition_is_allowed() -> None:
    validate_transition(MissionStatus.DRAFT, MissionStatus.VALIDATING)


def test_terminal_mission_transition_is_rejected() -> None:
    with pytest.raises(ValueError, match="INVALID_STATE_TRANSITION"):
        validate_transition(MissionStatus.COMPLETED, MissionStatus.RUNNING)


def test_task_retry_is_only_available_from_running() -> None:
    validate_transition(TaskStatus.RUNNING, TaskStatus.RETRYING)
    with pytest.raises(ValueError, match="INVALID_STATE_TRANSITION"):
        validate_transition(TaskStatus.CREATED, TaskStatus.RETRYING)