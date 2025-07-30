"""Auto-initialization helpers for environment-based setup."""

import os
from typing import Optional

from .exception_catcher import MiraSentinelExceptionCatcher
from .types import MiraSentinelConfig


def create_exception_catcher(config: MiraSentinelConfig) -> MiraSentinelExceptionCatcher:
    """Create an exception catcher instance."""
    return MiraSentinelExceptionCatcher(config)


def auto_initialize() -> Optional[MiraSentinelExceptionCatcher]:
    """Auto-initialization helper for environment-based setup."""
    sentinel_url = os.getenv("MIRA_SENTINEL_URL")
    service_name = os.getenv("MIRA_SERVICE_NAME") or os.getenv("SERVICE_NAME")
    repo = os.getenv("MIRA_REPO") or os.getenv("GITHUB_REPO")
    api_key = os.getenv("MIRA_API_KEY")
    
    if not sentinel_url or not service_name or not repo:
        print("[MiraSentinel] Auto-initialization skipped: missing required environment variables")
        print("[MiraSentinel] Required: MIRA_SENTINEL_URL, MIRA_SERVICE_NAME, MIRA_REPO")
        return None
    
    print("[MiraSentinel] Auto-initializing with environment variables")
    
    config = MiraSentinelConfig(
        sentinel_url=sentinel_url,
        service_name=service_name,
        repo=repo,
        api_key=api_key,
        enabled=os.getenv("MIRA_ENABLED", "true").lower() != "false"
    )
    
    catcher = MiraSentinelExceptionCatcher(config)
    catcher.initialize()
    return catcher