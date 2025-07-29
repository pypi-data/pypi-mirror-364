# LogonTG Python SDK - Installation Guide

This guide will help you install and set up the LogonTG Python SDK for your projects.

## 📋 Requirements

- **Python**: 3.7 or higher
- **Operating System**: Windows, macOS, or Linux
- **Internet Connection**: Required for API calls
- **LogonTG Account**: Register at [sruve.com](https://sruve.com)

## 🚀 Installation Methods

### Method 1: Install from PyPI (Recommended)

```bash
pip install logontg
```

### Method 2: Install from Source

```bash
git clone https://github.com/your-username/logontg.git
cd logontg
pip install -e .
```

### Method 3: Development Installation

```bash
git clone https://github.com/your-username/logontg.git
cd logontg
pip install -e ".[dev]"
```

## 🔧 Initial Setup

### 1. Create LogonTG Account

1. Visit [sruve.com](https://sruve.com)
2. Click "Sign Up" and create your account
3. Verify your email address

### 2. Connect Telegram

1. Start a chat with the LogonTG bot on Telegram
2. Follow the connection instructions
3. Your Telegram ID will be linked to your account

### 3. Get Your API Credentials

#### Option A: Using the SDK (Recommended)

```python
from logontg import LogonTGClient

# Register new account
client = LogonTGClient()
response = client.register(
    email="your.email@example.com",
    password="secure_password",
    telegram_id="your_telegram_id"  # Optional
)

# Login to get credentials
login_response = client.login("your.email@example.com", "secure_password")
api_key = login_response['user']['apiKey']
auth_token = login_response['token']

print(f"API Key: {api_key}")
print(f"Auth Token: {auth_token}")
```

#### Option B: Using the Web Dashboard

1. Log in to your LogonTG dashboard
2. Go to Profile/Settings
3. Copy your API key
4. Generate an auth token if needed

### 4. Environment Configuration

Create a `.env` file in your project:

```bash
LOGONTG_API_KEY=your_api_key_here
LOGONTG_AUTH_TOKEN=your_auth_token_here
LOGONTG_BASE_URL=https://sruve.com/api
```

## ✅ Verify Installation

Create a test file `test_logontg.py`:

```python
#!/usr/bin/env python3
from logontg import LogonTGClient

def test_installation():
    print("🔍 Testing LogonTG Python SDK installation...")
    
    # Test 1: Import test
    try:
        from logontg import LogonTGClient, Form, LogLevel
        print("✅ Import successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test 2: Client creation
    try:
        client = LogonTGClient()
        print("✅ Client creation successful")
    except Exception as e:
        print(f"❌ Client creation failed: {e}")
        return False
    
    # Test 3: API connection (requires credentials)
    api_key = "your_api_key_here"  # Replace with actual key
    
    if api_key != "your_api_key_here":
        try:
            logger = LogonTGClient(api_key=api_key)
            logger.info("🧪 SDK installation test successful!")
            print("✅ API connection successful")
            print("📱 Check your Telegram for the test message")
        except Exception as e:
            print(f"⚠️  API test failed: {e}")
            print("💡 This might be due to invalid credentials")
    else:
        print("⚠️  API test skipped (no credentials provided)")
    
    print("\n🎉 Installation verification completed!")
    return True

if __name__ == "__main__":
    test_installation()
```

Run the test:
```bash
python test_logontg.py
```

## 🐍 Virtual Environment Setup (Recommended)

### Using venv (Python 3.7+)

```bash
# Create virtual environment
python -m venv logontg-env

# Activate (Windows)
logontg-env\Scripts\activate

# Activate (macOS/Linux) 
source logontg-env/bin/activate

        # Install LogonTG SDK
        pip install logontg

# Verify installation
python -c "import logontg; print('✅ LogonTG SDK installed successfully')"
```

### Using conda

```bash
# Create environment
conda create -n logontg-env python=3.9

# Activate environment
conda activate logontg-env

        # Install SDK
        pip install logontg
```

## 📦 Dependency Management

### requirements.txt

Add to your `requirements.txt`:
```
logontg>=1.0.0
```

### setup.py

Add to your `setup.py`:
```python
setup(
    name="your-project",
    install_requires=[
        "logontg>=1.0.0",
    ],
)
```

### Pipfile (pipenv)

```toml
[packages]
logontg = ">=1.0.0"
```

### pyproject.toml (Poetry)

```toml
[tool.poetry.dependencies]
python = "^3.7"
logontg = "^1.0.0"
```

## 🔧 Framework-Specific Setup

### Django Integration

1. Install the SDK:
```bash
pip install logontg
```

2. Add to `settings.py`:
```python
# LogonTG Configuration
LOGONTG_API_KEY = os.getenv('LOGONTG_API_KEY')
LOGONTG_AUTH_TOKEN = os.getenv('LOGONTG_AUTH_TOKEN')

# Optional: Custom logging configuration
LOGGING = {
    'version': 1,
    'handlers': {
        'logontg': {
            'class': 'logontg.handlers.LogonTGHandler',
            'api_key': LOGONTG_API_KEY,
            'level': 'WARNING',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['logontg'],
            'level': 'WARNING',
        },
    },
}
```

### Flask Integration

```python
from flask import Flask
from logontg import LogonTGClient

app = Flask(__name__)

# Initialize LogonTG
logger = LogonTGClient(api_key=os.getenv('LOGONTG_API_KEY'))

@app.errorhandler(500)
def handle_error(error):
    logger.error(f"Flask Error: {str(error)}")
    return "Internal Server Error", 500
```

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from logontg import LogonTGClient
import os

app = FastAPI()
logger = LogonTGClient(api_key=os.getenv('LOGONTG_API_KEY'))

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"FastAPI Error: {str(exc)}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

## 🐳 Docker Setup

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment variables
ENV LOGONTG_API_KEY=""
ENV LOGONTG_AUTH_TOKEN=""

CMD ["python", "app.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    environment:
      - LOGONTG_API_KEY=${LOGONTG_API_KEY}
      - LOGONTG_AUTH_TOKEN=${LOGONTG_AUTH_TOKEN}
    ports:
      - "8000:8000"
```

## ☁️ Cloud Platform Setup

### Heroku

1. Add to `requirements.txt`:
```
logontg-python>=1.0.0
```

2. Set environment variables:
```bash
heroku config:set LOGONTG_API_KEY=your_api_key
heroku config:set LOGONTG_AUTH_TOKEN=your_auth_token
```

### AWS Lambda

```python
import os
from logontg import LogonTGClient

# Initialize outside handler for connection reuse
logger = LogonTGClient(api_key=os.getenv('LOGONTG_API_KEY'))

def lambda_handler(event, context):
    try:
        # Your function logic
        result = process_event(event)
        logger.info(f"Lambda execution successful: {result}")
        return result
    except Exception as e:
        logger.error(f"Lambda error: {str(e)}")
        raise
```

### Google Cloud Functions

```python
from logontg import LogonTGClient
import os

logger = LogonTGClient(api_key=os.getenv('LOGONTG_API_KEY'))

def main(request):
    try:
        # Your function logic
        result = process_request(request)
        logger.info(f"Function executed successfully")
        return result
    except Exception as e:
        logger.error(f"Function error: {str(e)}")
        return {"error": "Internal server error"}, 500
```

## 🔧 Troubleshooting

### Common Installation Issues

#### 1. Permission Errors

```bash
# Use --user flag
pip install --user logontg

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install logontg
```

#### 2. Python Version Issues

```bash
# Check Python version
python --version

# Use specific Python version
python3.9 -m pip install logontg
```

#### 3. Network/Proxy Issues

```bash
# Use proxy
pip install --proxy http://proxy.company.com:8080 logontg

# Use different index
pip install -i https://pypi.org/simple/ logontg
```

#### 4. SSL Certificate Issues

```bash
# Upgrade certificates
pip install --upgrade certifi

# Or bypass SSL (not recommended for production)
pip install --trusted-host pypi.org --trusted-host pypi.python.org logontg
```

### Runtime Issues

#### 1. Authentication Errors

- Verify your API key and auth token
- Check if your Telegram is connected
- Ensure you're using the correct base URL

#### 2. Rate Limiting

- Check your subscription limits
- Implement retry logic with exponential backoff
- Consider upgrading your plan

#### 3. Network Timeouts

```python
# Increase timeout
client = LogonTGClient(api_key="your_key", timeout=60)
```

## 📚 Next Steps

1. **Run Examples**: Try the examples in the `examples/` directory
2. **Read Documentation**: Check the full API documentation
3. **Join Community**: Connect with other users on Discord
4. **Start Building**: Integrate LogonTG into your projects!

## 🤝 Getting Help

- 📖 [Documentation](https://sruve.com/docs)
- 💬 [Discord Community](https://discord.gg/logontg)
- 🐛 [GitHub Issues](https://github.com/your-username/logontg/issues)
- 📧 Email: support@sruve.com

## ✨ What's Next?

After successful installation, check out:

- [`examples/quick_start.py`](examples/quick_start.py) - Get started in 5 minutes
- [`examples/basic_usage.py`](examples/basic_usage.py) - Complete walkthrough
- [`examples/advanced_forms.py`](examples/advanced_forms.py) - Advanced form features
- [`examples/logging_integration.py`](examples/logging_integration.py) - Production logging

Happy coding with LogonTG! 🚀 