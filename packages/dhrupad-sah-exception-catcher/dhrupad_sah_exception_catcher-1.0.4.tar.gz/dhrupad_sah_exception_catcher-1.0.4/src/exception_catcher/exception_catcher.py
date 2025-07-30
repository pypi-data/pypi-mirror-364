"""Mira Sentinel Exception Catcher for Python."""

import sys
import os
import traceback
import platform
import asyncio
import threading
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Callable, List
from urllib.parse import urljoin
import httpx

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from .types import (
    MiraSentinelConfig,
    ExceptionContext,
    SentinelResponse,
    ReportOptions,
    SystemContext,
    ErrorFilterCallback,
    ContextEnrichmentCallback,
)


class MiraSentinelExceptionCatcher:
    """
    Mira Sentinel Exception Catcher
    
    Automatically catches exceptions and reports them to Mira Sentinel with rich context.
    """
    
    def __init__(self, config: MiraSentinelConfig):
        """Initialize the exception catcher."""
        self.config = config
        self.is_initialized = False
        self.original_excepthook = None
        self.original_threading_excepthook = None
        self._client = None
        
        # Validate configuration
        self._validate_config()
        
        # Set up callbacks
        self.should_catch_error: ErrorFilterCallback = lambda error: True
        self.enrich_context: ContextEnrichmentCallback = lambda error, context: {}
        
        print(f"[MiraSentinel] Initializing exception catcher for {self.config.service_name}")
        print(f"[MiraSentinel] Reporting to: {self.config.sentinel_url}")
        print(f"[MiraSentinel] Repository: {self.config.repo}")
    
    def _validate_config(self) -> None:
        """Validate the configuration."""
        if not self.config.sentinel_url:
            raise ValueError("sentinel_url is required in Mira Sentinel configuration")
        
        if not self.config.service_name:
            raise ValueError("service_name is required in Mira Sentinel configuration")
        
        if not self.config.repo:
            raise ValueError("repo is required in Mira Sentinel configuration")
        
        if '/' not in self.config.repo:
            raise ValueError('repo must be in format "owner/repository"')
        
        # Validate URL
        try:
            from urllib.parse import urlparse
            result = urlparse(self.config.sentinel_url)
            if not all([result.scheme, result.netloc]):
                raise ValueError("sentinel_url must be a valid URL")
        except Exception:
            raise ValueError("sentinel_url must be a valid URL")
    
    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.config.timeout,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "dhrupad-sah-exception-catcher/1.0.0",
                    **({"Authorization": f"Bearer {self.config.api_key}"} if self.config.api_key else {})
                }
            )
        return self._client
    
    def initialize(self) -> None:
        """Initialize the exception catcher and start monitoring."""
        if self.is_initialized:
            print("[MiraSentinel] Exception catcher already initialized")
            return
        
        if not self.config.enabled:
            print("[MiraSentinel] Exception catcher disabled via configuration")
            return
        
        # Set up global exception handlers
        self._setup_global_handlers()
        
        self.is_initialized = True
        print("[MiraSentinel] Exception catcher initialized successfully")
    
    def shutdown(self) -> None:
        """Clean up and stop monitoring."""
        if not self.is_initialized:
            return
        
        print("[MiraSentinel] Shutting down exception catcher")
        
        # Restore original handlers
        self._remove_global_handlers()
        
        # Close HTTP client
        if self._client:
            asyncio.create_task(self._client.aclose())
        
        self.is_initialized = False
        print("[MiraSentinel] Exception catcher shut down")
    
    def _setup_global_handlers(self) -> None:
        """Set up global exception handlers."""
        # Store original handlers
        self.original_excepthook = sys.excepthook
        if hasattr(threading, 'excepthook'):
            self.original_threading_excepthook = threading.excepthook
        
        # Set our handlers
        sys.excepthook = self._handle_uncaught_exception
        if hasattr(threading, 'excepthook'):
            threading.excepthook = self._handle_threading_exception
    
    def _remove_global_handlers(self) -> None:
        """Remove global exception handlers."""
        # Restore original handlers
        if self.original_excepthook:
            sys.excepthook = self.original_excepthook
        
        if self.original_threading_excepthook and hasattr(threading, 'excepthook'):
            threading.excepthook = self.original_threading_excepthook
    
    def _handle_uncaught_exception(self, exc_type, exc_value, exc_traceback) -> None:
        """Handle uncaught exceptions."""
        try:
            # Create exception from the traceback info
            if exc_value is None:
                exc_value = exc_type()
            
            # Process the exception
            asyncio.create_task(
                self._process_exception(exc_value, "uncaughtException")
            )
            
        except Exception as e:
            print(f"[MiraSentinel] Failed to process uncaught exception: {e}")
        
        # Call original handler
        if self.original_excepthook:
            self.original_excepthook(exc_type, exc_value, exc_traceback)
        else:
            # Default behavior
            import traceback
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            sys.exit(1)
    
    def _handle_threading_exception(self, args) -> None:
        """Handle threading exceptions."""
        try:
            exc_value = args.exc_value
            if exc_value:
                asyncio.create_task(
                    self._process_exception(exc_value, "threadingException")
                )
        except Exception as e:
            print(f"[MiraSentinel] Failed to process threading exception: {e}")
        
        # Call original handler
        if self.original_threading_excepthook:
            self.original_threading_excepthook(args)
    
    async def _process_exception(self, error: Exception, exception_type: str) -> None:
        """Process an exception (check filters, build context, send)."""
        try:
            # Apply custom filtering
            if not self.should_catch_error(error):
                print(f"[MiraSentinel] Skipping error due to filter: {error}")
                return
            
            # Build rich context
            context = self._build_exception_context(
                error, 
                "automatic", 
                {"exception_type": exception_type, "timestamp": datetime.now(timezone.utc).isoformat()}
            )
            
            # Send to Mira Sentinel
            response = await self._send_to_sentinel(context)
            
            print(f"[MiraSentinel] Exception reported: {response.status} - {response.message}")
            if response.job_id:
                status_url = response.status_url or f"{self.config.sentinel_url}/jobs/{response.job_id}"
                print(f"[MiraSentinel] Track at: {status_url}")
                
        except Exception as report_error:
            print(f"[MiraSentinel] Failed to report exception: {report_error}")
    
    async def report_exception(
        self, 
        error: Exception, 
        options: Optional[ReportOptions] = None
    ) -> SentinelResponse:
        """Manually report an exception."""
        if options is None:
            options = ReportOptions()
        
        context = self._build_exception_context(error, "manual", options.context)
        
        # Apply service name override
        if options.service_name:
            context.service = options.service_name
        
        # Add tags and severity to context
        if options.tags or options.severity:
            context.context["custom"] = context.context.get("custom", {})
            if options.tags:
                context.context["custom"]["tags"] = options.tags
            if options.severity:
                context.context["custom"]["severity"] = options.severity
        
        return await self._send_to_sentinel(context)
    
    async def test_connection(self) -> bool:
        """Test the connection to Mira Sentinel without sending fake exceptions."""
        try:
            # Just test if the base URL is reachable
            base_url = self.config.sentinel_url.rstrip('/')
            
            response = await self.client.get(
                base_url,
                timeout=5.0
            )
            
            # If we get any response (even 404), the server is reachable
            return response.status_code < 500
            
        except Exception as e:
            print(f"[MiraSentinel] Connection test failed: {e}")
            return False
    
    def _build_exception_context(
        self,
        error: Exception,
        source: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> ExceptionContext:
        """Build rich exception context."""
        if additional_context is None:
            additional_context = {}
        
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Get system information
        if HAS_PSUTIL:
            try:
                memory_info = psutil.virtual_memory()._asdict()
            except Exception:
                memory_info = {"available": 0, "total": 0, "percent": 0}
        else:
            memory_info = {"available": 0, "total": 0, "percent": 0, "note": "psutil not available"}
        
        system_context = {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "hostname": platform.node(),
            "pid": os.getpid(),
            "memory_usage": memory_info,
            "cpu_count": os.cpu_count() or 1,
            "timestamp": timestamp
        }
        
        base_context = ExceptionContext(
            error=str(error),
            service=self.config.service_name,
            repo=self.config.repo,
            stacktrace=traceback.format_exc(),
            timestamp=timestamp,
            source=source,
            context={
                "system": system_context,
                "custom": additional_context
            }
        )
        
        # Apply custom context enrichment
        try:
            enriched_custom = self.enrich_context(error, base_context)
            base_context.context["custom"].update(enriched_custom)
        except Exception as e:
            print(f"[MiraSentinel] Context enrichment failed: {e}")
        
        return base_context
    
    async def _send_to_sentinel(self, context: ExceptionContext) -> SentinelResponse:
        """Send exception to Mira Sentinel with retry logic."""
        url = urljoin(self.config.sentinel_url.rstrip('/') + '/', 'webhook/exception-with-context')
        last_error = None
        
        for attempt in range(1, self.config.retry_attempts + 1):
            try:
                print(f"[MiraSentinel] Sending exception (attempt {attempt}/{self.config.retry_attempts})")
                
                response = await self.client.post(
                    url,
                    json=context.model_dump(),
                )
                response.raise_for_status()
                
                response_data = response.json()
                return SentinelResponse(**response_data)
                
            except Exception as e:
                last_error = e
                print(f"[MiraSentinel] Attempt {attempt} failed: {e}")
                
                if attempt < self.config.retry_attempts:
                    await asyncio.sleep(self.config.retry_delay * attempt)
        
        # All attempts failed
        raise Exception(f"Failed to send exception after {self.config.retry_attempts} attempts: {last_error}")
    
    def set_error_filter(self, callback: ErrorFilterCallback) -> None:
        """Set custom error filtering function."""
        self.should_catch_error = callback
    
    def set_context_enricher(self, callback: ContextEnrichmentCallback) -> None:
        """Set custom context enrichment function."""
        self.enrich_context = callback
    
    def get_config(self) -> MiraSentinelConfig:
        """Get current configuration (read-only)."""
        return self.config.model_copy()
    
    def is_ready(self) -> bool:
        """Check if the catcher is initialized."""
        return self.is_initialized