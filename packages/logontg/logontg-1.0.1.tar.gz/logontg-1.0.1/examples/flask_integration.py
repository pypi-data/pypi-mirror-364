"""
LogonTG Python SDK - Flask Web Framework Integration

This example shows how to integrate LogonTG logging with a Flask web application
for monitoring requests, errors, and application events.
"""

import os
import time
import traceback
from flask import Flask, request, jsonify, g
from functools import wraps
from logontg import logontg

# Initialize Flask app
app = Flask(__name__)

# Initialize LogonTG logger
api_key = os.getenv("LOGONTG_API_KEY", "your-api-key-here")
logger = logontg(api_key=api_key)

def generate_request_id():
    """Generate unique request ID"""
    return f"req_{int(time.time() * 1000)}"

@app.before_request
def before_request():
    """Log incoming requests"""
    g.start_time = time.time()
    g.request_id = generate_request_id()
    
    # Log request start (async logging in background)
    try:
        logger.debug_sync({
            "event": "request_start",
            "request_id": g.request_id,
            "method": request.method,
            "path": request.path,
            "ip": request.remote_addr,
            "user_agent": request.headers.get("User-Agent", "")[:100]  # Truncate long user agents
        })
    except Exception as e:
        # Don't let logging errors break the request
        print(f"Logging error: {e}")

@app.after_request
def after_request(response):
    """Log request completion"""
    try:
        duration = time.time() - g.start_time
        
        logger.log_sync({
            "event": "request_complete",
            "request_id": g.request_id,
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "response_size": len(response.get_data())
        })
    except Exception as e:
        print(f"Logging error: {e}")
    
    return response

def log_errors(f):
    """Decorator to log errors from route handlers"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # Log the error
            logger.error_sync({
                "event": "route_error",
                "request_id": getattr(g, 'request_id', 'unknown'),
                "path": request.path,
                "method": request.method,
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()
            })
            
            # Re-raise the exception
            raise e
    return decorated_function

# Routes

@app.route('/')
def home():
    """Home page"""
    logger.debug_sync(f"Home page accessed - Request ID: {g.request_id}")
    return jsonify({
        "message": "Welcome to LogonTG Flask Integration Demo",
        "request_id": g.request_id
    })

@app.route('/api/users', methods=['GET'])
@log_errors
def get_users():
    """Get users endpoint"""
    logger.debug_sync({
        "event": "fetching_users",
        "request_id": g.request_id
    })
    
    # Simulate database query
    time.sleep(0.1)  # Simulate processing time
    
    users = [
        {"id": 1, "name": "John Doe", "email": "john@example.com"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
    ]
    
    logger.log_sync({
        "event": "users_fetched",
        "request_id": g.request_id,
        "user_count": len(users)
    })
    
    return jsonify({"users": users})

@app.route('/api/users', methods=['POST'])
@log_errors
def create_user():
    """Create user endpoint"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('email'):
        logger.warn_sync({
            "event": "invalid_user_data",
            "request_id": g.request_id,
            "provided_data": data
        })
        return jsonify({"error": "Name and email are required"}), 400
    
    # Simulate user creation
    new_user = {
        "id": 3,
        "name": data['name'],
        "email": data['email']
    }
    
    logger.log_sync({
        "event": "user_created",
        "request_id": g.request_id,
        "user_id": new_user['id'],
        "user_name": new_user['name']
    })
    
    return jsonify({"user": new_user}), 201

@app.route('/api/error')
@log_errors
def trigger_error():
    """Endpoint that triggers an error for testing"""
    logger.debug_sync({
        "event": "error_endpoint_called",
        "request_id": g.request_id
    })
    
    # This will trigger the error logging decorator
    raise ValueError("This is a test error for demonstration")

@app.route('/api/slow')
def slow_endpoint():
    """Simulate a slow endpoint"""
    logger.debug_sync({
        "event": "slow_endpoint_start",
        "request_id": g.request_id
    })
    
    # Simulate slow processing
    time.sleep(2)
    
    logger.warn_sync({
        "event": "slow_endpoint_warning",
        "request_id": g.request_id,
        "message": "Endpoint took longer than expected"
    })
    
    return jsonify({"message": "This was a slow endpoint"})

@app.route('/api/business-event')
def business_event():
    """Simulate a business event"""
    logger.log_sync({
        "event": "purchase_completed",
        "request_id": g.request_id,
        "user_id": 12345,
        "product_id": "prod_premium",
        "amount": 99.99,
        "currency": "USD",
        "payment_method": "credit_card"
    })
    
    return jsonify({"message": "Purchase completed successfully"})

# Error handlers

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    logger.warn_sync({
        "event": "page_not_found",
        "request_id": getattr(g, 'request_id', 'unknown'),
        "path": request.path,
        "method": request.method,
        "ip": request.remote_addr
    })
    
    return jsonify({"error": "Page not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error_sync({
        "event": "internal_server_error",
        "request_id": getattr(g, 'request_id', 'unknown'),
        "path": request.path,
        "method": request.method,
        "error": str(error)
    })
    
    return jsonify({"error": "Internal server error"}), 500

def startup_logging():
    """Log application startup"""
    logger.log_sync({
        "event": "application_startup",
        "service": "flask_demo",
        "version": "1.0.0",
        "environment": os.getenv("FLASK_ENV", "development")
    })
    print("🚀 Flask application started with LogonTG integration")
    print("📱 All events will be logged to Telegram")
    print("\n📝 Available endpoints:")
    print("  GET  /                 - Home page")
    print("  GET  /api/users        - List users")
    print("  POST /api/users        - Create user")
    print("  GET  /api/error        - Trigger error (for testing)")
    print("  GET  /api/slow         - Slow endpoint")
    print("  GET  /api/business-event - Business event")

if __name__ == '__main__':
    startup_logging()
    
    print(f"\n💡 Make sure to set LOGONTG_API_KEY environment variable")
    print(f"💡 Current API key: {'Set' if api_key != 'your-api-key-here' else 'NOT SET'}")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000) 