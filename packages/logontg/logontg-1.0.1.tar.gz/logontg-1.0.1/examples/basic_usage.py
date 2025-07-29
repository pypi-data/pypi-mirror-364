"""
LogonTG Python SDK - Basic Usage Example

This example shows the basic logging functionality of the LogonTG Python SDK.
"""

import asyncio
import os
from logontg import logontg

async def logging_examples():
    """Demonstrate different logging scenarios"""
    
    # Get API key from environment or replace with your key
    api_key = os.getenv("LOGONTG_API_KEY", "your-api-key-here")
    
    if api_key == "your-api-key-here":
        print("⚠️  Please set LOGONTG_API_KEY environment variable or update the code")
        return
    
    # Initialize logger
    logger = logontg(api_key=api_key, debug=True)
    
    print("📝 LogonTG Basic Usage Examples")
    print("=" * 40)
    
    # 1. Simple string messages
    print("\n1️⃣ Simple String Messages")
    await logger.log("✅ Application started successfully")
    await logger.error("❌ Database connection failed") 
    await logger.warn("⚠️ High memory usage detected")
    await logger.debug("🔍 Processing request for user #123")
    
    # 2. Structured data logging
    print("\n2️⃣ Structured Data Logging")
    await logger.log({
        "event": "user_registration",
        "user_id": 12345,
        "email": "user@example.com",
        "source": "web_form",
        "timestamp": "2024-01-15T10:30:00Z"
    })
    
    # 3. Error with context
    print("\n3️⃣ Error Logging with Context")
    await logger.error({
        "error": "Database connection timeout",
        "host": "localhost",
        "port": 5432,
        "retry_count": 3,
        "timestamp": "2024-01-15T10:31:00Z"
    })
    
    # 4. Performance monitoring
    print("\n4️⃣ Performance Monitoring")
    import time
    start_time = time.time()
    
    # Simulate some work
    await asyncio.sleep(0.1)
    
    duration = time.time() - start_time
    await logger.debug({
        "operation": "user_profile_load",
        "duration_ms": round(duration * 1000, 2),
        "user_id": 456,
        "cache_hit": False
    })
    
    # 5. Application lifecycle events
    print("\n5️⃣ Application Lifecycle")
    await logger.log("🚀 Server starting on port 8000")
    await logger.log("🔗 Database connected successfully")
    await logger.log("🌐 API endpoints registered")
    await logger.log("✅ Application ready to serve requests")
    
    print("\n✅ All examples completed!")

def sync_logging_examples():
    """Demonstrate synchronous logging for non-async environments"""
    
    api_key = os.getenv("LOGONTG_API_KEY", "your-api-key-here")
    
    if api_key == "your-api-key-here":
        print("⚠️  Please set LOGONTG_API_KEY environment variable")
        return
    
    logger = logontg(api_key=api_key)
    
    print("\n📝 Synchronous Logging Examples")
    print("=" * 40)
    
    # Basic sync logging
    logger.log_sync("📊 Processing batch job...")
    logger.log_sync("📈 Processed 1000 records")
    logger.warn_sync("⚠️ Memory usage at 85%")
    logger.log_sync("✅ Batch job completed")
    
    # Error handling example
    try:
        # Simulate an error
        raise ValueError("Invalid configuration value")
    except Exception as e:
        logger.error_sync({
            "error": str(e),
            "error_type": type(e).__name__,
            "module": "config_loader"
        })
    
    print("✅ Sync examples completed!")

async def main():
    """Run all examples"""
    await logging_examples()
    sync_logging_examples()
    
    print("\n🎉 All examples completed successfully!")
    print("📱 Check your Telegram for all the log messages!")

if __name__ == "__main__":
    asyncio.run(main()) 