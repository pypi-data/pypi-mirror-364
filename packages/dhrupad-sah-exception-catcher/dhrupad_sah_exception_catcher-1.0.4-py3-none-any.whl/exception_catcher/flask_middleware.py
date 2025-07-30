"""Flask middleware integration for Mira Sentinel exception catching."""

from typing import Dict, Any, Optional, List, Callable
import asyncio
from datetime import datetime

try:
    from flask import Flask, request, jsonify, g
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False
    Flask = None
    request = None
    jsonify = None
    g = None

from .exception_catcher import MiraSentinelExceptionCatcher  
from .types import MiraSentinelConfig, RequestContextCallback


class FlaskMiraSentinel:
    """Flask integration for Mira Sentinel exception catching."""
    
    def __init__(
        self,
        config: MiraSentinelConfig,
        include_headers: bool = False,
        include_body: bool = False,
        skip_status_codes: Optional[List[int]] = None,
        extract_request_context: Optional[RequestContextCallback] = None
    ):
        """Initialize Flask integration."""
        if not HAS_FLASK:
            raise ImportError("Flask is required for FlaskMiraSentinel. Install with: pip install flask")
        
        self.config = config
        self.include_headers = include_headers
        self.include_body = include_body
        self.skip_status_codes = skip_status_codes or []
        self.extract_request_context = extract_request_context
        
        # Initialize the exception catcher
        self.catcher = MiraSentinelExceptionCatcher(config)
        self.catcher.initialize()
    
    def setup_app(self, app: Flask) -> None:
        """Set up error handling on Flask app."""
        
        @app.errorhandler(Exception)
        def handle_exception(error):
            """Handle all exceptions."""
            try:
                # Run async handler in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self._handle_flask_exception(error))
                finally:
                    loop.close()
                    
            except Exception as report_error:
                print(f"[MiraSentinel] Failed to report Flask exception: {report_error}")
            
            # Determine status code
            status_code = getattr(error, 'code', 500)
            if status_code < 400 or status_code >= 600:
                status_code = 500
            
            # Return error response
            error_message = str(error) if status_code < 500 else "Internal Server Error"
            return jsonify({"error": error_message}), status_code
        
        # Store reference for manual access
        app.mira_sentinel = self.catcher
    
    async def _handle_flask_exception(self, error: Exception) -> None:
        """Handle Flask route exceptions."""
        try:
            # Check if we should skip this status code
            status_code = getattr(error, 'code', 500)
            if status_code in self.skip_status_codes:
                return
            
            # Build request context
            request_context = self._build_request_context()
            
            # Report to Mira Sentinel
            await self.catcher.report_exception(error, {
                "context": {
                    "http": request_context,
                    "flask": {
                        "endpoint": request.endpoint if request else None,
                        "method": request.method if request else None,
                        "view_args": dict(request.view_args) if request and request.view_args else {},
                        "args": dict(request.args) if request else {}
                    }
                },
                "tags": ["flask", "http-error"],  
                "severity": "high" if status_code >= 500 else "medium"
            })
            
        except Exception as report_error:
            print(f"[MiraSentinel] Failed to report Flask exception: {report_error}")
    
    def _build_request_context(self) -> Dict[str, Any]:
        """Build request context from Flask request."""
        if not request:
            return {}
        
        context = {
            "method": request.method,
            "url": request.url,
            "client_ip": request.remote_addr,
            "user_agent": request.headers.get("User-Agent"),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Add headers if requested
        if self.include_headers:
            context["headers"] = dict(request.headers)
        
        # Add body if requested (be careful with sensitive data)
        if self.include_body:
            try:
                if request.is_json:
                    context["body"] = request.get_json()
                elif request.form:
                    context["body"] = dict(request.form)
                elif request.data:
                    context["body"] = request.data.decode("utf-8", errors="ignore")
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


def setup_flask_mira_sentinel(
    app: Flask,
    config: MiraSentinelConfig,
    include_headers: bool = False,
    include_body: bool = False,
    skip_status_codes: Optional[List[int]] = None,
    extract_request_context: Optional[RequestContextCallback] = None
) -> FlaskMiraSentinel:
    """Set up Mira Sentinel for a Flask application."""
    sentinel = FlaskMiraSentinel(
        config=config,
        include_headers=include_headers,
        include_body=include_body,
        skip_status_codes=skip_status_codes,
        extract_request_context=extract_request_context
    )
    
    sentinel.setup_app(app)
    return sentinel