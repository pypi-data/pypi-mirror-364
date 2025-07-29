"""
LogonTG Python SDK - Quick Start Example

This example demonstrates the basic usage of the LogonTG Python SDK
for simple logging to Telegram.
"""

import asyncio
from logontg import logontg

async def main():
    # Initialize the client with your API key
    logger = logontg(
        api_key="your-api-key-here",  # Replace with your actual API key
        debug=True  # Enable debug output
    )
    
    print("🚀 LogonTG Python SDK - Quick Start")
    print("=" * 40)
    
    # Send different types of logs
    print("📝 Sending logs...")
    
    # Info level log
    await logger.log("Application started successfully")
    
    # Error level log
    await logger.error("Database connection failed")
    
    # Warning level log  
    await logger.warn("High memory usage detected")
    
    # Debug level log
    await logger.debug("Processing user request #12345")
    
    # Log structured data
    await logger.log({
        "event": "user_action",
        "user_id": 12345,
        "action": "profile_update",
        "timestamp": "2024-01-15T10:30:00Z",
        "metadata": {
            "source": "web_app",
            "ip_address": "192.168.1.100"
        }
    })
    
    print("✅ All logs sent successfully!")
    print("\nCheck your Telegram for the messages!")

# Synchronous example (for non-async environments)
def sync_example():
    logger = logontg(api_key="your-api-key-here")
    
    print("\n📝 Synchronous logging example...")
    
    # Use sync methods
    logger.log_sync("Sync: Application started")
    logger.error_sync("Sync: Something went wrong")
    logger.warn_sync("Sync: Warning message")
    logger.debug_sync("Sync: Debug information")
    
    print("✅ Sync logs sent!")

if __name__ == "__main__":
    # Run async example
    asyncio.run(main())
    
    # Run sync example
    sync_example() 