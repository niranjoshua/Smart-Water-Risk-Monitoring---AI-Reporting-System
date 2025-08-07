import time
from functools import wraps
import os
from dotenv import load_dotenv
from typing import Callable, Any

load_dotenv()

class RateLimiter:
    def __init__(self, max_calls: int = 60, time_window: int = 60):
        self.max_calls = max_calls  # Maximum calls allowed in the time window
        self.time_window = time_window  # Time window in seconds
        self.calls = []  # List to track timestamps of calls

    def can_make_request(self) -> bool:
        """Check if a new request can be made within rate limits"""
        current_time = time.time()
        
        # Remove old timestamps outside the time window
        self.calls = [call_time for call_time in self.calls 
                     if current_time - call_time <= self.time_window]
        
        # Check if we're within the rate limit
        if len(self.calls) < self.max_calls:
            self.calls.append(current_time)
            return True
        return False

class APIKeyManager:
    @staticmethod
    def validate_api_key() -> bool:
        """Validate that API key is properly set and formatted"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        if not api_key.startswith(('sk-')):
            raise ValueError("Invalid OpenAI API key format")
        return True

def require_api_key(func: Callable) -> Callable:
    """Decorator to ensure API key is valid before making API calls"""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        APIKeyManager.validate_api_key()
        return func(*args, **kwargs)
    return wrapper

# Initialize rate limiter for OpenAI API calls
openai_rate_limiter = RateLimiter(max_calls=60, time_window=60)
