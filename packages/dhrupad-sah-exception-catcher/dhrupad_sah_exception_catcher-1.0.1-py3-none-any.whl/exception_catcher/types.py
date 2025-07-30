"""Type definitions for Mira Sentinel Exception Catcher."""

from typing import Dict, Any, Optional, Callable, List, Union
from pydantic import BaseModel, Field
from datetime import datetime


class MiraSentinelConfig(BaseModel):
    """Configuration for the exception catcher."""
    
    sentinel_url: str = Field(..., description="URL of your Mira Sentinel instance")
    service_name: str = Field(..., description="Name of the service (used for log correlation)")
    repo: str = Field(..., description="GitHub repository in format: owner/repo")
    api_key: Optional[str] = Field(None, description="Optional API key for authentication")
    enabled: bool = Field(True, description="Enable/disable automatic exception catching")
    timeout: float = Field(10.0, description="Timeout for HTTP requests to Sentinel (seconds)")
    retry_attempts: int = Field(3, description="Number of retry attempts")
    retry_delay: float = Field(1.0, description="Delay between retries (seconds)")


class SystemContext(BaseModel):
    """System context information."""
    
    python_version: str
    platform: str
    hostname: str
    pid: int
    memory_usage: Dict[str, Any]
    cpu_count: int
    timestamp: str


class ExceptionContext(BaseModel):
    """Exception context that gets sent to Mira Sentinel."""
    
    error: str = Field(..., description="The error message")
    service: str = Field(..., description="Service name")
    repo: str = Field(..., description="GitHub repository")
    stacktrace: str = Field(..., description="Full stack trace")
    timestamp: str = Field(..., description="Precise timestamp when exception occurred")
    source: str = Field(..., description="Source of the exception (automatic/manual)")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class SentinelResponse(BaseModel):
    """Response from Mira Sentinel webhook."""
    
    status: str = Field(..., description="Status of the request")
    message: str = Field(..., description="Response message")
    processed: bool = Field(..., description="Whether the request was processed")
    hash: Optional[str] = Field(None, description="Hash of the exception")
    job_id: Optional[str] = Field(None, description="Job ID for tracking")
    state: Optional[str] = Field(None, description="Current state")
    status_url: Optional[str] = Field(None, description="URL to check status")
    error: Optional[str] = Field(None, description="Error message if any")


class ReportOptions(BaseModel):
    """Options for manual exception reporting."""
    
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context to include")
    service_name: Optional[str] = Field(None, description="Override the service name")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    severity: Optional[str] = Field(None, description="Severity level")


class HTTPContext(BaseModel):
    """HTTP request context."""
    
    method: str
    url: str
    headers: Dict[str, str] = Field(default_factory=dict)
    query_params: Dict[str, Any] = Field(default_factory=dict)
    path_params: Dict[str, Any] = Field(default_factory=dict)
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: str
    request_id: Optional[str] = None


# Type aliases for callback functions
ErrorFilterCallback = Callable[[Exception], bool]
ContextEnrichmentCallback = Callable[[Exception, ExceptionContext], Dict[str, Any]]
RequestContextCallback = Callable[[Any], Dict[str, Any]]  # Any for request object