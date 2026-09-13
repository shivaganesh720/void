from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ObservabilityRecord:
    event_type: str
    payload: dict[str, Any]
    actor_id: str | None = None


@dataclass(frozen=True)
class RetentionPolicy:
    days_to_live: int = 30

    def should_expire(self, *, days_old: int | None = None, records: list[Any] | None = None) -> bool:
        if days_old is None and records is None:
            return False
        if days_old is not None:
            return days_old > self.days_to_live
        return bool(records and len(records) > self.days_to_live)


class ObservabilityService:
    """Simple structured event and metrics sink for mission traces."""

    def __init__(self) -> None:
        self._events: list[ObservabilityRecord] = []
        self._metrics: list[dict[str, Any]] = []

    def record_event(self, event_type: str, payload: dict[str, Any], *, actor_id: str | None = None) -> ObservabilityRecord:
        record = ObservabilityRecord(event_type=event_type, payload=payload, actor_id=actor_id)
        self._events.append(record)
        return record

    def record_metric(self, name: str, value: float, *, labels: dict[str, Any] | None = None) -> dict[str, Any]:
        record = {"name": name, "value": value, "labels": labels or {}}
        self._metrics.append(record)
        return record

    def latest_event(self) -> dict[str, Any]:
        if not self._events:
            return {}
        latest = self._events[-1]
        return {"event_type": latest.event_type, "payload": latest.payload, "actor_id": latest.actor_id}

    def list_metrics(self) -> list[dict[str, Any]]:
        return list(self._metrics)
