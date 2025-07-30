# dhrupad-sah-exception-catcher

Automatically catch and report exceptions to Mira Sentinel with rich context and log integration for AI-powered debugging and automatic fix generation.

## Features

- 🚨 **Automatic Exception Catching** - Monitors uncaught exceptions and unhandled rejections
- 📊 **Rich Context** - Collects system info, memory usage, and custom context
- 🔍 **Log Integration** - Correlates exceptions with log data for enhanced debugging
- 🤖 **AI-Powered Fixes** - Integrates with Claude Code for automatic issue resolution
- 📋 **GitHub Integration** - Automatically creates issues and pull requests
- 🔄 **Retry Logic** - Robust error reporting with configurable retries
- 🎯 **Flexible Filtering** - Custom error filtering and context enrichment

## Installation

```bash
# Using PDM (recommended)
pdm add dhrupad-sah-exception-catcher

# Using pip
pip install dhrupad-sah-exception-catcher

# With FastAPI support
pdm add dhrupad-sah-exception-catcher[fastapi]

# With Flask support  
pdm add dhrupad-sah-exception-catcher[flask]

# With all framework support
pdm add dhrupad-sah-exception-catcher[fastapi,flask]
```

## Quick Start

### FastAPI Integration (Recommended for APIs)

```python
from fastapi import FastAPI
from exception_catcher import setup_fastapi_mira_sentinel, MiraSentinelConfig
import os

app = FastAPI()

# Set up Mira Sentinel with environment variables
config = MiraSentinelConfig(
    sentinel_url=os.getenv("MIRA_SENTINEL_URL"),
    service_name=os.getenv("MIRA_SERVICE_NAME", "fastapi-service"),
    repo=os.getenv("MIRA_REPO", "company/fastapi-service")
)

# Set up automatic exception catching
sentinel = setup_fastapi_mira_sentinel(
    app,
    config,
    
    # Optional: Skip client errors
    skip_status_codes=[400, 401, 403, 404],
    
    # Optional: Extract custom context
    extract_request_context=lambda request: {
        "user_id": request.headers.get("x-user-id"),
        "trace_id": request.headers.get("x-trace-id")
    }
)

# Your routes - exceptions are automatically caught and reported
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await get_user_from_db(user_id)  # Any error here is caught
    return user

# Manual exception reporting is also available  
@app.get("/manual-report")
async def manual_report():
    try:
        await risky_operation()
    except Exception as error:
        await app.state.mira_sentinel.report_exception(error, {
            "context": {"operation": "risky"}
        })
        raise  # Re-raise to send HTTP error response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Basic Usage (Non-Framework Apps)

```python
from exception_catcher import MiraSentinelExceptionCatcher, MiraSentinelConfig

config = MiraSentinelConfig(
    sentinel_url="https://your-sentinel-instance.com",
    service_name="python-service",
    repo="company/python-service"
)

catcher = MiraSentinelExceptionCatcher(config)
catcher.initialize()

# That's it! All exceptions are now automatically caught and reported
```

### Environment-Based Auto-Initialization

```python
from exception_catcher import auto_initialize

# Set environment variables:
# MIRA_SENTINEL_URL=https://your-sentinel-instance.com
# MIRA_SERVICE_NAME=python-service
# MIRA_REPO=company/python-service

catcher = auto_initialize()
# Automatically initializes if environment variables are set
```

### Advanced Configuration

```python
from exception_catcher import MiraSentinelExceptionCatcher, MiraSentinelConfig

config = MiraSentinelConfig(
    sentinel_url="https://your-sentinel-instance.com",
    service_name="python-service", 
    repo="company/python-service",
    api_key="your-api-key",  # Optional authentication
    timeout=15.0,  # HTTP timeout in seconds
    retry_attempts=5,
    retry_delay=2.0
)

catcher = MiraSentinelExceptionCatcher(config)

# Custom error filtering
catcher.set_error_filter(lambda error: 
    # Skip test errors
    "test" not in str(error).lower()
)

# Enrich context with custom data
catcher.set_context_enricher(lambda error, context: {
    "user_id": get_current_user_id(),
    "request_id": get_current_request_id(),
    "version": os.getenv("APP_VERSION")
})

catcher.initialize()
```

## Manual Exception Reporting

```python
import asyncio
from exception_catcher import ReportOptions

try:
    # Some risky operation
    await process_payment(payment_data)
except Exception as error:
    # Manually report with additional context
    await catcher.report_exception(error, ReportOptions(
        context={
            "payment_id": payment_data.id,
            "user_id": payment_data.user_id,
            "amount": payment_data.amount
        },
        tags=["payment", "critical"],
        severity="high"
    ))
    
    raise  # Re-throw if needed
```

## Integration with Flask

```python
from flask import Flask
from exception_catcher import setup_flask_mira_sentinel, MiraSentinelConfig
import os

app = Flask(__name__)

config = MiraSentinelConfig(
    sentinel_url=os.getenv("MIRA_SENTINEL_URL"),
    service_name="flask-api",
    repo="company/flask-api"
)

# Set up automatic exception catching
sentinel = setup_flask_mira_sentinel(
    app,
    config,
    include_headers=True,
    skip_status_codes=[400, 401, 403, 404],
    extract_request_context=lambda request: {
        "user_id": request.headers.get("X-User-ID"),
        "session_id": request.headers.get("X-Session-ID")
    }
)

@app.route("/users/<int:user_id>")
def get_user(user_id):
    user = get_user_from_db(user_id)  # Any error here is caught
    return jsonify(user)

# Manual exception reporting
@app.route("/manual-report")
def manual_report():
    try:
        risky_operation()
    except Exception as error:
        # Note: Flask integration runs async in sync context
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                app.mira_sentinel.report_exception(error, {
                    "context": {"operation": "risky"}
                })
            )
        finally:
            loop.close()
        raise

if __name__ == "__main__":
    app.run(debug=True)
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MIRA_SENTINEL_URL` | URL of your Mira Sentinel instance | Yes |
| `MIRA_SERVICE_NAME` | Name of your service | Yes |
| `MIRA_REPO` | GitHub repository (owner/repo) | Yes |
| `MIRA_API_KEY` | API key for authentication | No |
| `MIRA_ENABLED` | Enable/disable (default: true) | No |

## Configuration Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `sentinel_url` | str | Mira Sentinel instance URL | Required |
| `service_name` | str | Service name for log correlation | Required |
| `repo` | str | GitHub repository (owner/repo) | Required |
| `api_key` | str | Optional API key | None |
| `enabled` | bool | Enable/disable catching | True |
| `timeout` | float | HTTP timeout (seconds) | 10.0 |
| `retry_attempts` | int | Retry attempts | 3 |
| `retry_delay` | float | Retry delay (seconds) | 1.0 |

## How It Works

1. **Exception Occurs** - Your service throws an exception
2. **Context Collection** - Rich context is automatically collected:
   - Error message and stack trace
   - System information (Python version, memory, CPU)
   - Timestamp for log correlation
   - Custom context from your application
3. **Sent to Mira Sentinel** - Exception data is sent to your Sentinel instance
4. **Log Integration** - Sentinel queries logs around the exception time
5. **AI Analysis** - Claude Code analyzes the exception + log context
6. **GitHub Integration** - Issue and PR are automatically created
7. **Timeline Analysis** - Full timeline of events leading to the exception

## Best Practices

### 1. Service Naming
Use consistent service names that match your log labels:

```python
# Good - matches log service label
service_name="api-gateway"

# Bad - doesn't match logs
service_name="my-awesome-service"
```

### 2. Error Filtering
Filter out noise to focus on actionable exceptions:

```python
def should_catch_error(error):
    # Skip test environments
    if os.getenv("ENV") == "test":
        return False
    
    # Skip known non-critical errors
    if "ConnectionResetError" in str(error):
        return False
    
    # Skip client errors for HTTP frameworks
    if hasattr(error, 'status_code') and 400 <= error.status_code < 500:
        return False
    
    return True

catcher.set_error_filter(should_catch_error)
```

### 3. Context Enrichment
Add meaningful context for better debugging:

```python
def enrich_context(error, context):
    return {
        # Business context
        "tenant_id": get_current_tenant(),
        "feature": get_current_feature(),
        
        # Technical context
        "version": os.getenv("APP_VERSION"),
        "deployment": os.getenv("DEPLOYMENT_ID"),
        
        # Performance context
        "response_time": get_response_time(),
        "queue_size": get_queue_size()
    }

catcher.set_context_enricher(enrich_context)
```

### 4. Graceful Shutdown
Always clean up on process exit:

```python
import atexit

catcher = MiraSentinelExceptionCatcher(config)
catcher.initialize()

def cleanup():
    catcher.shutdown()

atexit.register(cleanup)
```

## Testing

Test your integration:

```python
import asyncio
from exception_catcher import auto_initialize

async def test_integration():
    catcher = auto_initialize()
    
    if catcher:
        print("✅ Configuration loaded successfully")
        
        # Test connection
        is_connected = await catcher.test_connection()
        if is_connected:
            print("✅ Connection to Mira Sentinel successful")
        else:
            print("❌ Connection failed - check your MIRA_SENTINEL_URL")
    else:
        print("❌ Missing required environment variables")
        print("Required: MIRA_SENTINEL_URL, MIRA_SERVICE_NAME, MIRA_REPO")

# Run test
asyncio.run(test_integration())
```

## Development

```bash
# Clone the repository
git clone https://github.com/dhrupad-sah/python-exception-catcher
cd python-exception-catcher

# Install dependencies with PDM
pdm install

# Install with development dependencies
pdm install -d

# Run tests
pdm run pytest

# Format code
pdm run black src/
pdm run isort src/

# Type checking
pdm run mypy src/
```

## License

MIT

## Support

For support, please create an issue in the [GitHub repository](https://github.com/dhrupad-sah/python-exception-catcher).