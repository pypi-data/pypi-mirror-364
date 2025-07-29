"""LogonTG Python SDK - matches the JavaScript/Node version exactly"""

import requests
import json
import time
import threading
import sys
import signal
from typing import Dict, Any, Optional, List
from collections import defaultdict


class ErrorBatch:
    def __init__(self):
        self.errors: List[str] = []
        self.timestamp: float = time.time()
        self.stack_traces: List[str] = []


class UptimeOptions:
    def __init__(self):
        self.enabled: bool = False
        self.batch_window: int = 120000  # 2 minutes in milliseconds
        self.error_threshold: int = 3


class logontg:
    """
    LogonTG Python SDK
    
    Simple logging client with uptime monitoring capabilities.
    Matches the JavaScript/Node SDK functionality exactly.
    """
    
    def __init__(
        self,
        api_key: str,
        uptime: bool = False,
        base_url: str = "http://sruve.com/api",
        debug: bool = True
    ):
        """
        Initialize LogonTG client
        
        Args:
            api_key: Your LogonTG API key
            uptime: Enable uptime monitoring (requires Pro subscription)
            base_url: Base URL for the API
            debug: Enable debug logging
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.debug = debug
        self.uptime = UptimeOptions()
        self.error_batches: Dict[str, ErrorBatch] = {}
        self._original_excepthook = None
        
        # Initialize uptime monitoring if requested
        if uptime:
            self._check_pro_status_and_setup_monitoring()
    
    def _check_pro_status_and_setup_monitoring(self) -> None:
        """Check if user has Pro subscription and setup monitoring"""
        try:
            response = self._get('/logs/pro-status')
            if response.get('isPro'):
                self.uptime.enabled = True
                self._setup_error_listeners()
            else:
                self.uptime.enabled = False
                print("[logontg] Uptime monitoring requires a Pro subscription")
        except Exception as error:
            print(f"[logontg] Failed to verify pro status: {error}")
            self.uptime.enabled = False
    
    def _setup_error_listeners(self) -> None:
        """Setup global error monitoring"""
        # Store original exception handler
        self._original_excepthook = sys.excepthook
        
        # Override exception handler
        def exception_handler(exc_type, exc_value, exc_traceback):
            # Call original handler first
            self._original_excepthook(exc_type, exc_value, exc_traceback)
            
            # Handle the error
            import traceback
            stack_trace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self._handle_error(str(exc_value), stack_trace)
        
        sys.excepthook = exception_handler
    
    def _handle_error(self, error_message: str, stack_trace: str) -> None:
        """Handle and batch errors for uptime monitoring"""
        if not self.uptime.enabled:
            return
        
        error_key = self._get_error_key(error_message)
        now = time.time() * 1000  # Convert to milliseconds
        
        # Get or create error batch
        batch = self.error_batches.get(error_key)
        if not batch or (now - batch.timestamp * 1000) > self.uptime.batch_window:
            batch = ErrorBatch()
            batch.timestamp = now / 1000  # Store as seconds
        
        # Add error to batch
        batch.errors.append(error_message)
        batch.stack_traces.append(stack_trace)
        self.error_batches[error_key] = batch
        
        # Process batch if threshold reached
        if len(batch.errors) >= self.uptime.error_threshold:
            self._process_error_batch(batch)
            del self.error_batches[error_key]
    
    def _process_error_batch(self, batch: ErrorBatch) -> None:
        """Process error batch with LLM analysis"""
        try:
            # Get LLM analysis
            analysis = self._analyze_batch_with_llm(batch)
            
            # Log the analysis
            self.error({
                'type': 'uptime_alert',
                'analysis': analysis,
                'occurrences': len(batch.errors),
                'timeWindow': self.uptime.batch_window,
                'sampleError': batch.errors[0],
                'sampleStack': batch.stack_traces[0]
            })
        except Exception as error:
            print(f"[logontg] Failed to process error batch: {error}")
    
    def _analyze_batch_with_llm(self, batch: ErrorBatch) -> str:
        """Analyze error batch using LLM"""
        try:
            response = self._post('/logs/analyze-error', {
                'error': batch.errors[0],
                'stackTrace': batch.stack_traces[0]
            })
            
            return response.get('analysis', 'No analysis available')
        except Exception as error:
            print(f"[logontg] Error analyzing batch: {error}")
            return 'Error analysis unavailable'
    
    def _get_error_key(self, error: str) -> str:
        """Generate key for error batching"""
        return error.split('\n')[0].strip().lower()
    
    def set_uptime_monitoring(self, enabled: bool) -> None:
        """Enable or disable uptime monitoring"""
        if enabled and not self.uptime.enabled:
            self.uptime.enabled = True
            self._setup_error_listeners()
        else:
            self.uptime.enabled = False
            # Restore original exception handler
            if self._original_excepthook:
                sys.excepthook = self._original_excepthook
    
    # Core logging methods
    
    async def log(self, message: Any) -> None:
        """Send an info level log"""
        await self._send_log(message, 'info')
    
    async def error(self, message: Any) -> None:
        """Send an error level log"""
        await self._send_log(message, 'error')
    
    async def warn(self, message: Any) -> None:
        """Send a warning level log"""
        await self._send_log(message, 'warning')
    
    async def debug(self, message: Any) -> None:
        """Send a debug level log"""
        await self._send_log(message, 'debug')
    
    # Synchronous versions (for compatibility)
    
    def log_sync(self, message: Any) -> None:
        """Send an info level log (synchronous)"""
        self._send_log_sync(message, 'info')
    
    def error_sync(self, message: Any) -> None:
        """Send an error level log (synchronous)"""
        self._send_log_sync(message, 'error')
    
    def warn_sync(self, message: Any) -> None:
        """Send a warning level log (synchronous)"""
        self._send_log_sync(message, 'warning')
    
    def debug_sync(self, message: Any) -> None:
        """Send a debug level log (synchronous)"""
        self._send_log_sync(message, 'debug')
    
    # HTTP client methods
    
    def _post(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request"""
        full_url = f"{self.base_url}{url}"
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(full_url, json=data, headers=headers)
        
        # Handle response
        try:
            response_data = response.json()
        except:
            response_data = response.text
        
        if not response.ok:
            if response.status_code == 429:
                raise Exception('Rate limit exceeded. Please upgrade your plan.')
            error_msg = response_data.get('error', 'HTTP error') if isinstance(response_data, dict) else str(response_data)
            raise Exception(f"HTTP {response.status_code}: {error_msg}")
        
        return response_data
    
    def _get(self, url: str) -> Dict[str, Any]:
        """Make GET request"""
        full_url = f"{self.base_url}{url}"
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        response = requests.get(full_url, headers=headers)
        response_data = response.json()
        
        if not response.ok:
            error_msg = response_data.get('error', 'HTTP error')
            raise Exception(f"HTTP {response.status_code}: {error_msg}")
        
        return response_data
    
    async def _send_log(self, message: Any, level: str) -> None:
        """Send log message (async)"""
        import asyncio
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._send_log_sync, message, level)
    
    def _send_log_sync(self, message: Any, level: str) -> None:
        """Send log message (synchronous)"""
        try:
            payload = {
                'message': message if isinstance(message, str) else json.dumps(message),
                'level': level
            }
            
            self._post('/logs', payload)
            
        except Exception as error:
            if '429' in str(error):
                raise Exception('Rate limit exceeded. Please upgrade your plan.')
            print(f"Failed to send log: {error}")
            raise error
    
    def _logs(self, message: str) -> None:
        """Internal debug logging"""
        if self.debug:
            print(f"[logontg] {message}") 