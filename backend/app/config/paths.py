"""Root-anchored path resolution.

Every path the platform cares about is computed from the backend root
(``app/config/paths.py``'s location) rather than the process working
directory. Local shells, containers and Kubernetes pods therefore agree on
where logs, uploads and temporary files live regardless of where uvicorn
was launched.

Nothing here may import from other application packages.
"""

from pathlib import Path

# backend/ — parents: [0]=config, [1]=app, [2]=backend
BACKEND_ROOT: Path = Path(__file__).resolve().parents[2]

# Logs
LOG_DIR: Path = BACKEND_ROOT / "logs"
LOG_FILE: Path = LOG_DIR / "app.log"

# Storage (reserved — wired to real object storage in Phase 3)
STORAGE_DIR: Path = BACKEND_ROOT / "storage"
UPLOAD_DIR: Path = STORAGE_DIR / "uploads"
TMP_DIR: Path = STORAGE_DIR / "tmp"


def ensure_dirs() -> None:
    """Create directories the platform needs at boot (logs, storage)."""
    for directory in (LOG_DIR, STORAGE_DIR, UPLOAD_DIR, TMP_DIR):
        directory.mkdir(parents=True, exist_ok=True)
