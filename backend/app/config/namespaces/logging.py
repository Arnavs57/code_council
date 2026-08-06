"""Logging settings — typed projection of the root ``Settings``.

Env-var contract (flat, prefix ``CCAI_``)::

    CCAI_LOG_LEVEL        DEBUG | INFO | WARNING | ERROR | CRITICAL
    CCAI_LOG_TO_FILE      write rotating JSON file logs
    CCAI_LOG_FILE         log file path (absolute, or relative to backend root)
    CCAI_LOG_MAX_BYTES    per-file size before rotation
    CCAI_LOG_BACKUP_COUNT retained rotated files
"""

from pathlib import Path

from pydantic import BaseModel, ConfigDict

from app.config import paths


class LoggingSettings(BaseModel):
    """Structured logging configuration."""

    model_config = ConfigDict(frozen=True)

    level: str
    to_file: bool
    file: Path
    max_bytes: int
    backup_count: int

    @property
    def resolved_file(self) -> Path:
        """The absolute log path (anchored to the backend root if relative)."""
        if self.file.is_absolute():
            return self.file
        return paths.BACKEND_ROOT / self.file
