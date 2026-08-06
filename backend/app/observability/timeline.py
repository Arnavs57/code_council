"""Timeline engine for generating timestamped execution events."""

from datetime import datetime, timezone
from typing import Any, Dict, List


class TimelineEngine:
    """Manages execution timeline events during a PR review run."""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []

    def add_event(self, title: str, description: str = "", event_type: str = "INFO") -> Dict[str, Any]:
        """Record a timestamped timeline event."""
        now = datetime.now(timezone.utc)
        event = {
            "timestamp": now.strftime("%H:%M:%S"),
            "iso_time": now.isoformat(),
            "title": title,
            "description": description,
            "event_type": event_type,
        }
        self.events.append(event)
        return event

    def get_events(self) -> List[Dict[str, Any]]:
        """Return all recorded timeline events."""
        return self.events
