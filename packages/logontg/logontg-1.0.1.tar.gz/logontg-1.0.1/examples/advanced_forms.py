"""
LogonTG Python SDK - Advanced Logging & Uptime Monitoring Example

This example demonstrates advanced logging features and uptime monitoring
capabilities of the LogonTG Python SDK.
"""

import asyncio
import os
import time
import random
from logontg import logontg

async def advanced_logging_demo():
    """Demonstrate advanced logging patterns"""
    
    api_key = os.getenv("LOGONTG_API_KEY", "your-api-key-here")
    
    if api_key == "your-api-key-here":
        print("⚠️  Please set LOGONTG_API_KEY environment variable")
        return
    
    # Initialize with uptime monitoring (requires Pro subscription)
    logger = logontg(
        api_key=api_key,
        uptime=True,  # Enable uptime monitoring
        debug=True
    )
    
    print("🔍 LogonTG Advanced Logging & Uptime Monitoring")
    print("=" * 50)
    
    # 1. Application Performance Monitoring
    print("\n1️⃣ Performance Monitoring")
    
    for i in range(3):
        start_time = time.time()
        
        # Simulate database query
        await asyncio.sleep(random.uniform(0.05, 0.2))
        
        duration = time.time() - start_time
        
        await logger.debug({
            "event": "database_query",
            "query_id": f"q_{i+1}",
            "duration_ms": round(duration * 1000, 2),
            "table": "users",
            "rows_affected": random.randint(50, 500),
            "cache_hit": random.choice([True, False])
        })
    
    # 2. User Activity Tracking
    print("\n2️⃣ User Activity Tracking")
    
    user_actions = [
        {"action": "login", "user_id": 123, "ip": "192.168.1.100"},
        {"action": "profile_update", "user_id": 123, "fields": ["email", "name"]},
        {"action": "file_upload", "user_id": 123, "file_size": 2048576},
        {"action": "logout", "user_id": 123, "session_duration": 1800}
    ]
    
    for action in user_actions:
        await logger.log({
            "event": "user_activity",
            "timestamp": time.time(),
            **action
        })
        await asyncio.sleep(0.1)
    
    # 3. Business Metrics Logging
    print("\n3️⃣ Business Metrics")
    
    metrics = [
        {"metric": "revenue", "value": 1250.75, "currency": "USD"},
        {"metric": "new_signups", "value": 23, "period": "daily"},
        {"metric": "conversion_rate", "value": 0.045, "funnel": "landing_to_signup"},
        {"metric": "churn_rate", "value": 0.02, "period": "monthly"}
    ]
    
    for metric in metrics:
        await logger.log({
            "event": "business_metric",
            "timestamp": time.time(),
            **metric
        })
    
    # 4. Error Scenarios (for uptime monitoring demo)
    print("\n4️⃣ Error Scenarios (Uptime Monitoring)")
    
    # Simulate various errors
    error_scenarios = [
        {"error": "Database connection timeout", "service": "postgres", "severity": "high"},
        {"error": "API rate limit exceeded", "service": "external_api", "severity": "medium"},
        {"error": "Disk space low", "service": "file_storage", "severity": "high"},
        {"error": "Memory usage critical", "service": "application", "severity": "critical"}
    ]
    
    for scenario in error_scenarios:
        await logger.error({
            "event": "system_error",
            "timestamp": time.time(),
            "environment": "production",
            **scenario
        })
        await asyncio.sleep(0.5)
    
    # 5. Structured Logging with Context
    print("\n5️⃣ Structured Logging with Request Context")
    
    # Simulate API request processing
    request_id = f"req_{int(time.time())}"
    
    await logger.debug({
        "event": "request_start",
        "request_id": request_id,
        "method": "POST",
        "endpoint": "/api/v1/users",
        "user_agent": "Mozilla/5.0...",
        "ip_address": "203.0.113.1"
    })
    
    # Processing steps
    await logger.debug({
        "event": "validation_complete",
        "request_id": request_id,
        "validation_time_ms": 15
    })
    
    await logger.debug({
        "event": "database_write",
        "request_id": request_id,
        "table": "users",
        "operation": "INSERT",
        "execution_time_ms": 45
    })
    
    await logger.log({
        "event": "request_complete",
        "request_id": request_id,
        "status_code": 201,
        "total_time_ms": 125,
        "response_size_bytes": 256
    })
    
    print("\n✅ Advanced logging examples completed!")

def sync_monitoring_example():
    """Demonstrate synchronous monitoring for background jobs"""
    
    api_key = os.getenv("LOGONTG_API_KEY", "your-api-key-here")
    
    if api_key == "your-api-key-here":
        print("⚠️  Please set LOGONTG_API_KEY environment variable")
        return
    
    logger = logontg(api_key=api_key)
    
    print("\n📊 Background Job Monitoring")
    print("=" * 30)
    
    # Simulate a batch processing job
    job_id = f"job_{int(time.time())}"
    total_items = 1000
    
    logger.log_sync({
        "event": "job_start",
        "job_id": job_id,
        "job_type": "data_processing",
        "total_items": total_items
    })
    
    # Process in chunks
    for chunk in range(0, total_items, 100):
        processed = min(chunk + 100, total_items)
        
        logger.debug_sync({
            "event": "job_progress",
            "job_id": job_id,
            "processed": processed,
            "total": total_items,
            "percentage": round((processed / total_items) * 100, 1)
        })
        
        # Simulate processing time
        time.sleep(0.1)
    
    logger.log_sync({
        "event": "job_complete",
        "job_id": job_id,
        "status": "success",
        "items_processed": total_items,
        "duration_seconds": 1.0
    })
    
    print("✅ Background job monitoring completed!")

async def uptime_monitoring_demo():
    """Demonstrate uptime monitoring features"""
    
    api_key = os.getenv("LOGONTG_API_KEY", "your-api-key-here")
    
    logger = logontg(
        api_key=api_key,
        uptime=True,  # This requires Pro subscription
        debug=True
    )
    
    print("\n🔍 Uptime Monitoring Demo")
    print("=" * 30)
    
    # Simulate repeated errors (will trigger batching)
    print("Generating similar errors to trigger batching...")
    
    for i in range(5):
        try:
            # Simulate the same error multiple times
            raise ConnectionError("Database connection failed")
        except Exception as e:
            await logger.error({
                "error": str(e),
                "error_type": type(e).__name__,
                "attempt": i + 1,
                "service": "database"
            })
        
        await asyncio.sleep(1)
    
    print("✅ Uptime monitoring demo completed!")
    print("💡 With Pro subscription, similar errors are batched and analyzed by AI")

async def main():
    """Run all advanced examples"""
    
    print("🚀 Starting LogonTG Advanced Examples...")
    
    await advanced_logging_demo()
    sync_monitoring_example()
    await uptime_monitoring_demo()
    
    print("\n🎉 All advanced examples completed!")
    print("📱 Check your Telegram for comprehensive logging!")
    print("\n💡 Pro Tips:")
    print("  - Use structured logging for better analysis")
    print("  - Include request IDs for tracing")
    print("  - Monitor business metrics alongside technical metrics")
    print("  - Enable uptime monitoring for production systems")

if __name__ == "__main__":
    asyncio.run(main()) 