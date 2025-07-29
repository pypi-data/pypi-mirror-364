# LogonTG Python SDK - Integration Guide

This guide shows you how to effectively integrate LogonTG into your applications and get the most out of the Python SDK.

## 🚀 Getting Started in 5 Minutes

### 1. Installation & Setup
```bash
pip install logontg
```

### 2. Quick Registration & First Log
```python
from logontg import LogonTGClient

# Register (one-time setup)
client = LogonTGClient()
registration = client.register(
    email="your.email@example.com",
    password="secure_password"
)

# Login and get credentials
login = client.login("your.email@example.com", "secure_password")
api_key = login['user']['apiKey']

# Send your first log to Telegram!
logger = LogonTGClient(api_key=api_key)
logger.info("🎉 Hello from LogonTG Python SDK!")
```

### 3. Create Your First Form
```python
auth_token = login['token']
form_client = LogonTGClient(auth_token=auth_token)

form = form_client.create_simple_form(
    title="Contact Us",
    fields=[
        {"label": "Name", "type": "text", "required": True},
        {"label": "Email", "type": "email", "required": True},
        {"label": "Message", "type": "textarea", "required": True}
    ]
)

print(f"🌐 Your form: https://sruve.com/f/{form.form_id}")
```

That's it! You now have a working form that sends responses to your Telegram.

## 🎯 Real-World Integration Patterns

### 1. 📊 Application Monitoring

Transform your application monitoring with real-time Telegram alerts:

```python
import psutil
import time
from logontg import LogonTGClient

class ServerMonitor:
    def __init__(self, api_key):
        self.logger = LogonTGClient(api_key=api_key)
        self.last_alert = {}
    
    def check_system_health(self):
        # CPU monitoring
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 80:
            self.alert_if_needed('cpu', f"🔥 High CPU usage: {cpu_percent}%")
        
        # Memory monitoring
        memory = psutil.virtual_memory()
        if memory.percent > 85:
            self.alert_if_needed('memory', f"💾 High memory usage: {memory.percent}%")
        
        # Disk monitoring
        disk = psutil.disk_usage('/')
        free_gb = disk.free / (1024**3)
        if free_gb < 5:  # Less than 5GB free
            self.alert_if_needed('disk', f"💿 Low disk space: {free_gb:.1f}GB remaining")
    
    def alert_if_needed(self, alert_type, message):
        # Prevent spam - only alert once per hour
        current_time = time.time()
        if alert_type not in self.last_alert or current_time - self.last_alert[alert_type] > 3600:
            self.logger.warning(message)
            self.last_alert[alert_type] = current_time

# Usage
monitor = ServerMonitor("your_api_key")

# Run monitoring loop
while True:
    monitor.check_system_health()
    time.sleep(60)  # Check every minute
```

### 2. 🛍️ E-commerce Integration

Get instant notifications for your online store:

```python
from logontg import LogonTGClient
from datetime import datetime

class EcommerceNotifier:
    def __init__(self, api_key):
        self.logger = LogonTGClient(api_key=api_key)
    
    def new_order(self, order_data):
        """Notify about new orders"""
        message = f"""
🛒 **NEW ORDER RECEIVED!**

Order ID: {order_data['id']}
Customer: {order_data['customer_name']}
Email: {order_data['customer_email']}
Total: ${order_data['total']:.2f}
Items: {order_data['item_count']}

Payment: {order_data['payment_method']}
Status: {order_data['status']}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        self.logger.info(message)
    
    def payment_failed(self, order_data, error):
        """Alert on payment failures"""
        self.logger.error(f"💳 Payment failed for order {order_data['id']}: {error}")
    
    def inventory_low(self, product_name, quantity):
        """Alert on low inventory"""
        if quantity <= 5:
            self.logger.warning(f"📦 Low inventory alert: {product_name} ({quantity} remaining)")
    
    def daily_summary(self, sales_data):
        """Send daily sales summary"""
        message = f"""
📈 **DAILY SALES SUMMARY**

Date: {sales_data['date']}
Orders: {sales_data['order_count']}
Revenue: ${sales_data['total_revenue']:.2f}
Top Product: {sales_data['top_product']}

Compared to yesterday:
Orders: {sales_data['order_change']:+d}
Revenue: ${sales_data['revenue_change']:+.2f}
        """
        self.logger.info(message)

# Usage in your e-commerce application
notifier = EcommerceNotifier("your_api_key")

# In your order processing code
def process_order(order_data):
    try:
        # Process payment
        payment_result = process_payment(order_data)
        
        # Update inventory
        update_inventory(order_data['items'])
        
        # Send success notification
        notifier.new_order(order_data)
        
    except PaymentError as e:
        notifier.payment_failed(order_data, str(e))
    except InventoryError as e:
        notifier.inventory_low(e.product, e.quantity)
```

### 3. 🔐 Security Monitoring

Monitor your application's security in real-time:

```python
import hashlib
import json
from datetime import datetime
from logontg import LogonTGClient

class SecurityMonitor:
    def __init__(self, api_key):
        self.logger = LogonTGClient(api_key=api_key)
        self.failed_attempts = {}
    
    def failed_login(self, username, ip_address, user_agent):
        """Track failed login attempts"""
        key = f"{username}:{ip_address}"
        
        if key not in self.failed_attempts:
            self.failed_attempts[key] = 0
        
        self.failed_attempts[key] += 1
        
        # Alert after 3 failed attempts
        if self.failed_attempts[key] >= 3:
            self.logger.warning(f"""
🚨 **SECURITY ALERT: Multiple Failed Logins**

Username: {username}
IP Address: {ip_address}
Attempts: {self.failed_attempts[key]}
User Agent: {user_agent}
Time: {datetime.now().isoformat()}

Action: Consider blocking this IP address.
            """)
    
    def suspicious_activity(self, user_id, activity, details):
        """Report suspicious user activity"""
        self.logger.error(f"""
⚠️ **SUSPICIOUS ACTIVITY DETECTED**

User ID: {user_id}
Activity: {activity}
Details: {json.dumps(details, indent=2)}
Time: {datetime.now().isoformat()}

Please investigate immediately.
        """)
    
    def admin_action(self, admin_user, action, target):
        """Log important admin actions"""
        self.logger.info(f"""
👨‍💼 **ADMIN ACTION**

Admin: {admin_user}
Action: {action}
Target: {target}
Time: {datetime.now().isoformat()}
        """)

# Usage
security = SecurityMonitor("your_api_key")

# In your authentication system
def login_attempt(username, password, request):
    if not verify_password(username, password):
        security.failed_login(
            username=username,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        return False
    
    # Clear failed attempts on successful login
    key = f"{username}:{request.remote_addr}"
    if key in security.failed_attempts:
        del security.failed_attempts[key]
    
    return True
```

### 4. 📝 Customer Feedback System

Create beautiful forms and get instant feedback:

```python
from logontg import LogonTGClient, FormField, FormFieldType

class FeedbackSystem:
    def __init__(self, auth_token, api_key):
        self.form_client = LogonTGClient(auth_token=auth_token)
        self.logger = LogonTGClient(api_key=api_key)
        
    def create_product_feedback_form(self, product_name):
        """Create a feedback form for a specific product"""
        form = self.form_client.create_simple_form(
            title=f"Feedback: {product_name}",
            description=f"Help us improve {product_name} with your feedback",
            fields=[
                {"label": "Your Name", "type": "text", "required": True},
                {"label": "Email", "type": "email", "required": True},
                {"label": "Overall Rating", "type": "rating", "required": True},
                {"label": "What did you like most?", "type": "textarea", "required": False},
                {"label": "What could be improved?", "type": "textarea", "required": False},
                {"label": "Would you recommend this product?", "type": "radio", 
                 "options": ["Definitely", "Probably", "Not Sure", "Probably Not", "Definitely Not"], 
                 "required": True}
            ],
            theme="gradient"
        )
        
        self.logger.info(f"📋 Created feedback form for {product_name}: https://sruve.com/f/{form.form_id}")
        return form
    
    def create_support_ticket_form(self):
        """Create a support ticket form"""
        form = self.form_client.create_simple_form(
            title="Support Request",
            description="Need help? We're here to assist you!",
            fields=[
                {"label": "Name", "type": "text", "required": True},
                {"label": "Email", "type": "email", "required": True},
                {"label": "Subject", "type": "select", 
                 "options": ["Bug Report", "Feature Request", "Account Issue", "Billing", "Other"], 
                 "required": True},
                {"label": "Priority", "type": "radio", 
                 "options": ["Low", "Medium", "High", "Urgent"], 
                 "required": True},
                {"label": "Description", "type": "textarea", "required": True},
                {"label": "Attach Screenshot", "type": "file", "required": False}
            ],
            theme="modern"
        )
        
        return form
    
    def process_feedback(self, form_submissions):
        """Process and analyze feedback submissions"""
        ratings = [s.get('overall_rating', 0) for s in form_submissions]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # Alert on low ratings
        if avg_rating < 3.0:
            self.logger.warning(f"⭐ Low average rating detected: {avg_rating:.1f}/5")
        
        # Summary report
        self.logger.info(f"""
📊 **FEEDBACK SUMMARY**

Total Responses: {len(form_submissions)}
Average Rating: {avg_rating:.1f}/5
Positive Feedback: {len([r for r in ratings if r >= 4])}/{len(ratings)}

Latest feedback needs attention.
        """)

# Usage
feedback_system = FeedbackSystem("your_auth_token", "your_api_key")

# Create feedback forms for your products
product_form = feedback_system.create_product_feedback_form("Awesome Widget Pro")
support_form = feedback_system.create_support_ticket_form()

print(f"Product feedback: https://sruve.com/f/{product_form.form_id}")
print(f"Support form: https://sruve.com/f/{support_form.form_id}")
```

## 🔧 Advanced Integration Techniques

### 1. Environment-Based Configuration

```python
import os
from logontg import LogonTGClient

class LogonTGConfig:
    def __init__(self):
        self.api_key = os.getenv('LOGONTG_API_KEY')
        self.auth_token = os.getenv('LOGONTG_AUTH_TOKEN')
        self.environment = os.getenv('ENVIRONMENT', 'development')
        
        # Different settings per environment
        if self.environment == 'production':
            self.log_level = 'WARNING'  # Only warnings and errors in prod
            self.base_url = 'https://sruve.com/api'
        else:
            self.log_level = 'INFO'  # All logs in development
            self.base_url = 'http://localhost:3001/api'
    
    def get_logger(self):
        if not self.api_key:
            return None  # Graceful degradation
        
        return LogonTGClient(
            api_key=self.api_key,
            base_url=self.base_url,
            debug=(self.environment != 'production')
        )
    
    def get_form_client(self):
        if not self.auth_token:
            return None
        
        return LogonTGClient(
            auth_token=self.auth_token,
            base_url=self.base_url
        )

# Usage
config = LogonTGConfig()
logger = config.get_logger()

if logger:
    logger.info("Application started")
else:
    print("LogonTG not configured - running without notifications")
```

### 2. Django Integration

```python
# settings.py
LOGONTG_API_KEY = os.getenv('LOGONTG_API_KEY')
LOGONTG_AUTH_TOKEN = os.getenv('LOGONTG_AUTH_TOKEN')

# Custom logging handler
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'logontg': {
            'level': 'ERROR',
            'class': 'myapp.logging.LogonTGHandler',
            'api_key': LOGONTG_API_KEY,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['logontg'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# myapp/logging.py
import logging
from logontg import LogonTGClient

class LogonTGHandler(logging.Handler):
    def __init__(self, api_key, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = LogonTGClient(api_key=api_key) if api_key else None
    
    def emit(self, record):
        if not self.client:
            return
        
        message = self.format(record)
        
        if record.levelno >= logging.ERROR:
            self.client.error(message)
        elif record.levelno >= logging.WARNING:
            self.client.warning(message)

# views.py
from django.shortcuts import render
from logontg import LogonTGClient
from django.conf import settings

def contact_view(request):
    if request.method == 'POST':
        # Process form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Send notification
        if settings.LOGONTG_API_KEY:
            logger = LogonTGClient(api_key=settings.LOGONTG_API_KEY)
            logger.info(f"📧 New contact form submission from {name} ({email})")
        
        return render(request, 'contact_success.html')
    
    return render(request, 'contact.html')
```

### 3. Async/Await Support

```python
import asyncio
import aiohttp
from logontg import LogonTGClient

class AsyncLogonTG:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://sruve.com/api"
    
    async def log_async(self, message, level="info"):
        """Send log asynchronously"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/logs",
                json={"message": message, "level": level},
                headers={"x-api-key": self.api_key}
            ) as response:
                return await response.json()

# Usage in async applications
async def process_batch_data(data_batch):
    logger = AsyncLogonTG("your_api_key")
    
    try:
        # Process data
        results = await process_data_async(data_batch)
        
        # Log success
        await logger.log_async(f"✅ Processed {len(results)} items successfully")
        
    except Exception as e:
        # Log error
        await logger.log_async(f"❌ Batch processing failed: {str(e)}", "error")
```

### 4. Rate Limiting & Retry Logic

```python
import time
import random
from logontg import LogonTGClient, RateLimitError

class ResilientLogger:
    def __init__(self, api_key, max_retries=3):
        self.client = LogonTGClient(api_key=api_key)
        self.max_retries = max_retries
    
    def log_with_retry(self, message, level="info", delay_base=1):
        """Log with exponential backoff retry"""
        for attempt in range(self.max_retries):
            try:
                if level == "info":
                    return self.client.info(message)
                elif level == "warning":
                    return self.client.warning(message)
                elif level == "error":
                    return self.client.error(message)
                
            except RateLimitError as e:
                if attempt == self.max_retries - 1:
                    print(f"Failed to send log after {self.max_retries} attempts")
                    return False
                
                # Exponential backoff with jitter
                delay = (delay_base * (2 ** attempt)) + random.uniform(0, 1)
                print(f"Rate limited, retrying in {delay:.1f}s...")
                time.sleep(delay)
            
            except Exception as e:
                print(f"Failed to send log: {e}")
                return False
        
        return False

# Usage
logger = ResilientLogger("your_api_key")
logger.log_with_retry("Important message that must be delivered", "warning")
```

## 🎨 Best Practices

### 1. **Use Environment Variables**
```python
import os
from logontg import LogonTGClient

# Never hardcode credentials
client = LogonTGClient(
    api_key=os.getenv('LOGONTG_API_KEY'),
    auth_token=os.getenv('LOGONTG_AUTH_TOKEN')
)
```

### 2. **Implement Graceful Degradation**
```python
def get_logger():
    try:
        return LogonTGClient(api_key=os.getenv('LOGONTG_API_KEY'))
    except Exception:
        return None  # Fallback to None if LogonTG unavailable

logger = get_logger()

def log_event(message):
    if logger:
        logger.info(message)
    else:
        print(f"Log: {message}")  # Fallback to console
```

### 3. **Filter Log Levels Appropriately**
```python
class SmartLogger:
    def __init__(self, api_key, environment='production'):
        self.client = LogonTGClient(api_key=api_key)
        self.environment = environment
    
    def info(self, message):
        # Only send info logs in development
        if self.environment == 'development':
            self.client.info(message)
    
    def warning(self, message):
        # Always send warnings
        self.client.warning(message)
    
    def error(self, message):
        # Always send errors
        self.client.error(message)
```

### 4. **Structure Your Log Messages**
```python
def structured_log(event_type, user_id=None, details=None):
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "event": event_type,
        "environment": os.getenv('ENVIRONMENT', 'unknown')
    }
    
    if user_id:
        log_data["user_id"] = user_id
    
    if details:
        log_data["details"] = details
    
    logger.info(json.dumps(log_data, indent=2))

# Usage
structured_log("user_login", user_id="12345", details={"ip": "192.168.1.1"})
```

## 🚀 Going Live: Production Checklist

### ✅ Security
- [ ] Use environment variables for all credentials
- [ ] Never commit API keys to version control
- [ ] Use HTTPS in production
- [ ] Implement rate limiting in your application

### ✅ Monitoring
- [ ] Set up health checks
- [ ] Monitor API usage to stay within limits
- [ ] Implement retry logic for failed requests
- [ ] Set up alerting for critical errors

### ✅ Performance
- [ ] Use async logging where possible
- [ ] Batch non-critical logs
- [ ] Filter log levels appropriately
- [ ] Monitor response times

### ✅ Reliability
- [ ] Implement graceful degradation
- [ ] Test error scenarios
- [ ] Set up backup notification methods
- [ ] Document your integration

## 🎉 You're Ready!

With this guide, you now have everything you need to:

- ✅ **Monitor** your applications in real-time
- ✅ **Collect** customer feedback effortlessly  
- ✅ **Alert** your team instantly about issues
- ✅ **Track** important business events
- ✅ **Scale** your notification system reliably

## 📚 What's Next?

1. **Start Small**: Begin with basic logging and expand gradually
2. **Explore Examples**: Check out the `examples/` directory for more ideas
3. **Join Community**: Connect with other users on Discord
4. **Upgrade When Ready**: Unlock Pro features like AI error analysis
5. **Share Your Success**: Tell us how LogonTG helped your project!

## 🤝 Need Help?

- 📖 [API Documentation](https://sruve.com/docs)
- 💬 [Discord Community](https://discord.gg/logontg)  
- 📧 Email: support@sruve.com
- 🐛 [GitHub Issues](https://github.com/your-username/logontg/issues)

Happy building with LogonTG! 🚀🎉 