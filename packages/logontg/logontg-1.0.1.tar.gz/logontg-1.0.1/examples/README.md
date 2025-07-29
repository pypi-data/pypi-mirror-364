# LogonTG Python SDK Examples

This directory contains comprehensive examples showing how to use the LogonTG Python SDK for logging and uptime monitoring.

## Examples Overview

### 🚀 [quick_start.py](quick_start.py)
**Perfect for beginners!** The simplest way to get started with LogonTG logging.
- Basic async and sync logging
- Different log levels (info, error, warning, debug)
- Structured data logging

### 📊 [basic_usage.py](basic_usage.py)
**Essential patterns** for everyday logging scenarios.
- Application lifecycle logging
- Performance monitoring
- Error logging with context
- Structured data examples

### 🔍 [advanced_forms.py](advanced_forms.py) → [advanced_logging.py](advanced_forms.py)
**Advanced features** including uptime monitoring and complex logging patterns.
- Performance monitoring
- Business metrics logging
- Error batching and uptime monitoring (Pro feature)
- Request tracing

### 🔗 [logging_integration.py](logging_integration.py)
**Framework integration** with Python's built-in logging system.
- Custom LogonTG logging handler
- Integration with standard Python logging
- Structured logging wrapper
- Context management

### 🌐 [flask_integration.py](flask_integration.py)
**Web framework integration** showing real-world usage patterns.
- Request/response logging
- Error handling and logging
- Business event tracking
- Performance monitoring

## Running the Examples

### Prerequisites
1. **Install the SDK**:
   ```bash
   pip install logontg
   ```

2. **Get your API key** from your LogonTG dashboard

3. **Set environment variable** (recommended):
   ```bash
   export LOGONTG_API_KEY="your-api-key-here"
   ```

### Quick Start
```bash
# Run the simplest example
python quick_start.py

# Or try basic usage patterns
python basic_usage.py
```

### Flask Web App Example
```bash
# Install Flask if not already installed
pip install flask

# Run the Flask integration example
python flask_integration.py

# Visit http://localhost:5000 and try different endpoints
```

## Key Features Demonstrated

### 🎯 Simple Logging
- **Four log levels**: info, error, warning, debug
- **Async and sync** methods available
- **Any data type**: strings, objects, arrays

### 📊 Structured Logging
- **Rich context**: Include metadata with every log
- **Request tracing**: Follow requests through your application
- **Business metrics**: Track important business events

### 🔍 Uptime Monitoring (Pro Feature)
- **Automatic error detection**: Catches unhandled exceptions
- **Error batching**: Groups similar errors over time windows
- **AI analysis**: LLM-powered error insights and solutions

### 🌐 Framework Integration
- **Web frameworks**: Flask, Django, FastAPI examples
- **Background jobs**: Celery, cron job monitoring
- **Standard logging**: Works with Python's logging module

## Example Scenarios

### Startup Monitoring
```python
from logontg import logontg

logger = logontg("your-api-key")

await logger.log("🚀 Application starting...")
await logger.log("✅ Database connected")
await logger.log("🌐 Server ready on port 8000")
```

### Error Tracking
```python
try:
    result = risky_operation()
    await logger.log(f"✅ Operation successful: {result}")
except Exception as e:
    await logger.error({
        "error": str(e),
        "operation": "risky_operation",
        "context": {"user_id": 123}
    })
```

### Performance Monitoring
```python
import time

start = time.time()
# ... your code ...
duration = time.time() - start

await logger.debug({
    "operation": "database_query",
    "duration_ms": duration * 1000,
    "rows_returned": 150
})
```

### Business Events
```python
await logger.log({
    "event": "purchase_completed",
    "user_id": 12345,
    "amount": 99.99,
    "product": "premium_plan"
})
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `LOGONTG_API_KEY` | Your LogonTG API key | Yes |
| `LOGONTG_DEBUG` | Enable debug output | No |

## Tips for Production

1. **Use structured logging** for better analysis
2. **Include request IDs** for tracing
3. **Set appropriate log levels** to avoid spam
4. **Monitor business metrics** alongside technical metrics
5. **Enable uptime monitoring** for critical systems (Pro feature)

## Getting Help

- 📧 **Email**: support@sruve.com
- 🌐 **Website**: https://sruve.com
- 📖 **Documentation**: https://sruve.com/docs

## Contributing

Found a bug or want to add an example? Contributions are welcome! Please submit issues and pull requests to our GitHub repository.

---

**Happy Logging!** 🎉 