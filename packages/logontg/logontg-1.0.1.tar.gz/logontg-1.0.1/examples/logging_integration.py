"""
LogonTG Python SDK - Logging Framework Integration

This example shows how to integrate LogonTG with Python's built-in
logging framework and popular third-party logging libraries.
"""

import asyncio
import logging
import sys
import json
from logontg import logontg

class LogonTGHandler(logging.Handler):
    """Custom logging handler that sends logs to LogonTG"""
    
    def __init__(self, api_key, level=logging.NOTSET):
        super().__init__(level)
        self.logontg_client = logontg(api_key=api_key)
    
    def emit(self, record):
        """Send log record to LogonTG"""
        try:
            # Format the log message
            message = {
                "timestamp": record.created,
                "level": record.levelname.lower(),
                "logger": record.name,
                "message": self.format(record),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            
            # Add exception info if present
            if record.exc_info:
                message["exception"] = self.formatException(record.exc_info)
            
            # Send to LogonTG based on level
            if record.levelno >= logging.ERROR:
                self.logontg_client.error_sync(message)
            elif record.levelno >= logging.WARNING:
                self.logontg_client.warn_sync(message)
            elif record.levelno >= logging.INFO:
                self.logontg_client.log_sync(message)
            else:
                self.logontg_client.debug_sync(message)
                
        except Exception:
            # Don't let logging errors break the application
            self.handleError(record)

def setup_integrated_logging():
    """Setup Python logging with LogonTG integration"""
    
    api_key = "your-api-key-here"  # Replace with your API key
    
    # Create logger
    logger = logging.getLogger('myapp')
    logger.setLevel(logging.DEBUG)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # Create LogonTG handler
    logontg_handler = LogonTGHandler(api_key)
    logontg_handler.setLevel(logging.WARNING)  # Only send warnings and errors to Telegram
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(logontg_handler)
    
    return logger

async def direct_integration_example():
    """Example of direct LogonTG integration"""
    
    api_key = "your-api-key-here"  # Replace with your API key
    logger = logontg(api_key=api_key)
    
    print("📱 Direct LogonTG Integration Example")
    print("=" * 40)
    
    # Application startup
    await logger.log("🚀 Application starting...")
    
    # Simulate application workflow
    try:
        await logger.debug("Loading configuration...")
        await logger.debug("Connecting to database...")
        await logger.log("✅ Database connected successfully")
        
        await logger.debug("Initializing services...")
        await logger.log("✅ All services initialized")
        
        # Simulate some business logic
        await logger.log({
            "event": "user_action",
            "action": "purchase",
            "user_id": 12345,
            "amount": 99.99,
            "product": "premium_subscription"
        })
        
        # Simulate a warning
        await logger.warn({
            "event": "performance_warning",
            "message": "Database query took longer than expected",
            "query_time_ms": 1500,
            "threshold_ms": 1000
        })
        
    except Exception as e:
        await logger.error({
            "event": "application_error",
            "error": str(e),
            "error_type": type(e).__name__
        })
    
    print("✅ Direct integration example completed!")

def python_logging_integration_example():
    """Example using Python's built-in logging framework"""
    
    print("\n📊 Python Logging Framework Integration")
    print("=" * 40)
    
    # Setup integrated logging
    logger = setup_integrated_logging()
    
    # Use standard Python logging
    logger.info("Application started with integrated logging")
    logger.debug("This debug message goes to console only")
    logger.warning("This warning goes to both console and Telegram")
    
    # Log with extra context
    logger.info("User logged in", extra={
        "user_id": 456,
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0..."
    })
    
    # Simulate an error with exception
    try:
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error("Division by zero error occurred", exc_info=True)
    
    print("✅ Python logging integration example completed!")

class StructuredLogger:
    """A structured logger wrapper for LogonTG"""
    
    def __init__(self, api_key, service_name="myapp"):
        self.client = logontg(api_key=api_key)
        self.service_name = service_name
        self.context = {}
    
    def set_context(self, **kwargs):
        """Set context that will be included in all logs"""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear the current context"""
        self.context = {}
    
    async def log(self, message, **extra):
        """Log info level message with context"""
        await self.client.log({
            "service": self.service_name,
            "message": message,
            **self.context,
            **extra
        })
    
    async def error(self, message, **extra):
        """Log error level message with context"""
        await self.client.error({
            "service": self.service_name,
            "message": message,
            **self.context,
            **extra
        })
    
    async def warn(self, message, **extra):
        """Log warning level message with context"""
        await self.client.warn({
            "service": self.service_name,
            "message": message,
            **self.context,
            **extra
        })
    
    async def debug(self, message, **extra):
        """Log debug level message with context"""
        await self.client.debug({
            "service": self.service_name,
            "message": message,
            **self.context,
            **extra
        })

async def structured_logging_example():
    """Example of structured logging wrapper"""
    
    print("\n🏗️ Structured Logging Example")
    print("=" * 30)
    
    api_key = "your-api-key-here"  # Replace with your API key
    logger = StructuredLogger(api_key, service_name="ecommerce_api")
    
    # Set global context
    logger.set_context(
        version="1.2.3",
        environment="production",
        datacenter="us-east-1"
    )
    
    # Log with automatic context inclusion
    await logger.log("Service started")
    
    # Add request-specific context
    logger.set_context(
        request_id="req_12345",
        user_id=789,
        endpoint="/api/orders"
    )
    
    await logger.debug("Processing order request")
    await logger.log("Order validated successfully", order_id="ord_456")
    await logger.warn("Inventory low", product_id="prod_123", stock=2)
    await logger.log("Order completed", order_id="ord_456", total=149.99)
    
    # Clear request context
    logger.clear_context()
    logger.set_context(version="1.2.3", environment="production")
    
    await logger.log("Request processing completed")
    
    print("✅ Structured logging example completed!")

async def main():
    """Run all integration examples"""
    
    print("🔗 LogonTG Logging Integration Examples")
    print("=" * 50)
    
    await direct_integration_example()
    python_logging_integration_example()
    await structured_logging_example()
    
    print("\n🎉 All integration examples completed!")
    print("📱 Check your Telegram for all the log messages!")
    print("\n💡 Integration Tips:")
    print("  - Use LogonTG for critical alerts and business events")
    print("  - Keep console/file logging for debugging")
    print("  - Add structured context for better log analysis")
    print("  - Set appropriate log levels to avoid spam")

if __name__ == "__main__":
    asyncio.run(main()) 