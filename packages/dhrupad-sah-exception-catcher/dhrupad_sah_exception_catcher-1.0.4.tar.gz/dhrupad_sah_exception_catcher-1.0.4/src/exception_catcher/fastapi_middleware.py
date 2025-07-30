"""FastAPI middleware integration for Mira Sentinel exception catching."""

from typing import Dict, Any, Optional, List, Callable
import asyncio
from datetime import datetime

try:
    from fastapi import FastAPI, Request, Response
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.responses import JSONResponse
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    FastAPI = None
    Request = None
    Response = None
    BaseHTTPMiddleware = None
    JSONResponse = None

from .exception_catcher import MiraSentinelExceptionCatcher
from .types import MiraSentinelConfig, HTTPContext, RequestContextCallback


class FastAPIMiraSentinel:
    """FastAPI integration for Mira Sentinel exception catching."""
    
    def __init__(
        self,
        config: MiraSentinelConfig,
        include_headers: bool = False,
        include_body: bool = False,
        skip_status_codes: Optional[List[int]] = None,
        extract_request_context: Optional[RequestContextCallback] = None
    ):
        """Initialize FastAPI integration."""
        if not HAS_FASTAPI:
            raise ImportError("FastAPI is required for FastAPIMiraSentinel. Install with: pip install fastapi")
        
        self.config = config
        self.include_headers = include_headers
        self.include_body = include_body
        self.skip_status_codes = skip_status_codes or []
        self.extract_request_context = extract_request_context
        
        # Initialize the exception catcher
        self.catcher = MiraSentinelExceptionCatcher(config)
        self.catcher.initialize()
    
    def setup_middleware(self, app: FastAPI) -> None:
        """Set up middleware on FastAPI app."""
        
        class MiraSentinelMiddleware(BaseHTTPMiddleware):
            def __init__(self, app, sentinel_instance):
                super().__init__(app)
                self.sentinel = sentinel_instance
            
            async def dispatch(self, request: Request, call_next):
                try:
                    response = await call_next(request)
                    return response
                except Exception as error:
                    # Handle the exception
                    await self.sentinel._handle_fastapi_exception(error, request)
                    
                    # Determine status code
                    status_code = getattr(error, 'status_code', 500)
                    if status_code < 400 or status_code >= 600:
                        status_code = 500
                    
                    # Return error response
                    error_message = str(error) if status_code < 500 else "Internal Server Error"
                    return JSONResponse(
                        status_code=status_code,
                        content={"error": error_message}
                    )
        
        app.add_middleware(MiraSentinelMiddleware, sentinel_instance=self)
        
        # Store reference for manual access
        app.state.mira_sentinel = self.catcher
    
    async def _handle_fastapi_exception(self, error: Exception, request: Request) -> None:
        """Handle FastAPI route exceptions."""
        try:
            # Check if we should skip this status code
            status_code = getattr(error, 'status_code', 500)
            if status_code in self.skip_status_codes:
                return
            
            # Build request context
            request_context = await self._build_request_context(request)
            
            # Report to Mira Sentinel
            await self.catcher.report_exception(error, {
                "context": {
                    "http": request_context,
                    "fastapi": {
                        "route": getattr(request, 'url', {}).path if hasattr(request, 'url') else '',
                        "method": request.method,
                        "path_params": dict(request.path_params) if hasattr(request, 'path_params') else {},
                        "query_params": dict(request.query_params) if hasattr(request, 'query_params') else {}
                    }
                },
                "tags": ["fastapi", "http-error"],
                "severity": "high" if status_code >= 500 else "medium"
            })
            
        except Exception as report_error:
            print(f"[MiraSentinel] Failed to report FastAPI exception: {report_error}")
    
    async def _build_request_context(self, request: Request) -> Dict[str, Any]:
        """Build request context from FastAPI request."""
        context = {
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Add headers if requested
        if self.include_headers:
            context["headers"] = dict(request.headers)
        
        # Add body if requested (be careful with sensitive data)
        if self.include_body:
            try:
                # This might consume the body, so be careful
                body = await request.body()
                if body:
                    context["body"] = body.decode("utf-8", errors="ignore")
            except Exception:
                context["body"] = "<unable to read body>"
        
        # Add custom request context
        if self.extract_request_context:
            try:
                custom_context = self.extract_request_context(request)
                context.update(custom_context)
            except Exception as e:
                print(f"[MiraSentinel] Request context extraction failed: {e}")
        
        return context
    
    def shutdown(self) -> None:
        """Shutdown the exception catcher."""
        self.catcher.shutdown()


def setup_fastapi_mira_sentinel(
    app: FastAPI,
    config: MiraSentinelConfig,
    include_headers: bool = False,
    include_body: bool = False,
    skip_status_codes: Optional[List[int]] = None,
    extract_request_context: Optional[RequestContextCallback] = None
) -> FastAPIMiraSentinel:
    """Set up Mira Sentinel for a FastAPI application."""
    sentinel = FastAPIMiraSentinel(
        config=config,
        include_headers=include_headers,
        include_body=include_body,
        skip_status_codes=skip_status_codes,
        extract_request_context=extract_request_context
    )
    
    sentinel.setup_middleware(app)
    return sentinel