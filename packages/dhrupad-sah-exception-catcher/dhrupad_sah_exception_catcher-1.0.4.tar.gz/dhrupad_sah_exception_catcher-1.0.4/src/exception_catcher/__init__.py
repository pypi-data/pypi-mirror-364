"""
dhrupad-sah-exception-catcher

Automatically catch and report exceptions to Mira Sentinel with rich context
and log integration for enhanced debugging capabilities.
"""

from .exception_catcher import MiraSentinelExceptionCatcher
from .types import (
    MiraSentinelConfig,
    ExceptionContext,
    SentinelResponse,
    ReportOptions,
)
from .auto_init import auto_initialize, create_exception_catcher

__version__ = "1.0.4"
__all__ = [
    "MiraSentinelExceptionCatcher",
    "MiraSentinelConfig", 
    "ExceptionContext",
    "SentinelResponse",
    "ReportOptions",
    "auto_initialize",
    "create_exception_catcher",
]

# Try to import framework integrations
try:
    from .fastapi_middleware import FastAPIMiraSentinel, setup_fastapi_mira_sentinel
    __all__.extend(["FastAPIMiraSentinel", "setup_fastapi_mira_sentinel"])
except ImportError:
    pass

try:
    from .flask_middleware import FlaskMiraSentinel, setup_flask_mira_sentinel
    __all__.extend(["FlaskMiraSentinel", "setup_flask_mira_sentinel"])
except ImportError:
    pass