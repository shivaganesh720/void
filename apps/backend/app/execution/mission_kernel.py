from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class TaskState(StrEnum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    PAUSED = "PAUSED"
    RETRYING = "RETRYING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    BLOCKED = "BLOCKED"
    SKIPPED = "SKIPPED"
    TIMED_OUT = "TIMED_OUT"


@dataclass
class TaskNode:
    id: UUID
    name: str
    dependencies: list[UUID] = field(default_factory=list)
    state: TaskState = TaskState.CREATED
    agent_id: str | None = None
    input_data: dict[str, Any] = field(default_factory=dict)
    output_data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300

    def can_transition_to(self, target: TaskState) -> bool:
        """Validate state transitions according to the state machine."""
        if self.state == TaskState.CANCELLED:
            return False  # Terminal state
        if self.state == TaskState.SUCCEEDED:
            return False  # Terminal state
        if self.state == TaskState.FAILED and target != TaskState.RETRYING:
            return False
        return True

    def transition(self, target: TaskState, error: str | None = None) -> None:
        if not self.can_transition_to(target):
            raise ValueError(f"Invalid transition from {self.state} to {target}")
        self.state = target
        if error:
            self.error = error


@dataclass
class WorkGraph:
    mission_id: UUID
    nodes: dict[UUID, TaskNode] = field(default_factory=dict)

    def add_task(self, task: TaskNode) -> None:
        self.nodes[task.id] = task

    def validate(self) -> None:
        """Reject malformed dependency graphs before scheduling can inspect them."""
        missing = {
            dependency
            for task in self.nodes.values()
            for dependency in task.dependencies
            if dependency not in self.nodes
        }
        if missing:
            missing_ids = ", ".join(sorted(str(item) for item in missing))
            raise ValueError(f"INVALID_DEPENDENCY:{missing_ids}")

        visiting: set[UUID] = set()
        visited: set[UUID] = set()

        def visit(task_id: UUID) -> None:
            if task_id in visiting:
                raise ValueError("WORK_GRAPH_CYCLE")
            if task_id in visited:
                return
            visiting.add(task_id)
            for dependency in self.nodes[task_id].dependencies:
                visit(dependency)
            visiting.remove(task_id)
            visited.add(task_id)

        for task_id in self.nodes:
            visit(task_id)

    def get_ready_tasks(self) -> list[TaskNode]:
        """Returns tasks whose dependencies have all SUCCEEDED."""
        self.validate()
        ready = []
        for task in self.nodes.values():
            if task.state in (TaskState.CREATED, TaskState.QUEUED):
                deps_met = all(self.nodes[dep_id].state == TaskState.SUCCEEDED for dep_id in task.dependencies)
                if deps_met:
                    ready.append(task)
        return ready

    def mark_blocked(self) -> None:
        """Marks tasks as BLOCKED if their dependencies FAILED."""
        self.validate()
        for task in self.nodes.values():
            if task.state in (TaskState.CREATED, TaskState.QUEUED):
                deps_failed = any(self.nodes[dep_id].state in (TaskState.FAILED, TaskState.CANCELLED, TaskState.TIMED_OUT) for dep_id in task.dependencies)
                if deps_failed:
                    task.transition(TaskState.BLOCKED, error="Dependency failed or cancelled.")

    def is_complete(self) -> bool:
        """Returns True if no tasks are pending or running."""
        terminal_states = {TaskState.SUCCEEDED, TaskState.FAILED, TaskState.CANCELLED, TaskState.TIMED_OUT, TaskState.BLOCKED, TaskState.SKIPPED}
        return all(task.state in terminal_states for task in self.nodes.values())
