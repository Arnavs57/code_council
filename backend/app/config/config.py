"""Central configuration access point.

Modules import the ``settings`` singleton from here — the single import for
the whole platform. Nothing else reads environment variables or env files.
"""

from functools import lru_cache

from app.config.bootstrap import build_settings
from app.config.settings import Settings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Build (and cache) the frozen application settings singleton."""
    return build_settings()


settings: Settings = get_settings()
