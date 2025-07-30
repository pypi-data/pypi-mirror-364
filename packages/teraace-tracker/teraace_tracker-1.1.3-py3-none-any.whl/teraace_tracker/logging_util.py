"""
Logging utility for Teraace tracker.
"""

import logging
import sys
from typing import Optional


class TeraaceLogger:
    """Logger utility for Teraace tracker operations."""
    
    def __init__(self, name: str = "teraace_tracker", level: int = logging.INFO):
        """Initialize logger with specified name and level."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Avoid duplicate handlers
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(message, **kwargs)
    
    def log_buffer_status(self, current_size: int, max_size: int):
        """Log buffer status."""
        self.debug(f"Buffer status: {current_size}/{max_size} events")
    
    def log_flush_attempt(self, event_count: int):
        """Log flush attempt."""
        self.info(f"🔄 Teraace Tracker: Flushing {event_count} events from buffer")
    
    def log_flush_success(self, event_count: int):
        """Log successful flush."""
        self.info(f"✅ Teraace Tracker: Successfully flushed {event_count} events")
    
    def log_flush_error(self, event_count: int, error: str):
        """Log flush error."""
        self.error(f"❌ Teraace Tracker: Failed to flush {event_count} events - {error}")
    
    def log_api_call(self, endpoint: str, status_code: Optional[int] = None):
        """Log API call details."""
        if status_code:
            self.info(f"🌐 Teraace API call to {endpoint} returned status {status_code}")
        else:
            self.info(f"🚀 Teraace API: Making request to {endpoint}")
    
    def log_api_attempt(self, endpoint: str, event_count: int, attempt: int, max_attempts: int):
        """Log API attempt with retry info."""
        self.info(f"📡 Teraace API: Sending {event_count} events to {endpoint} (attempt {attempt}/{max_attempts})")
    
    def log_api_success(self, endpoint: str, event_count: int):
        """Log successful API call."""
        self.info(f"✅ Teraace API: Successfully sent {event_count} events to {endpoint}")
    
    def log_api_error(self, endpoint: str, event_count: int, status_code: int, error: str):
        """Log API error."""
        self.error(f"❌ Teraace API: Failed to send {event_count} events to {endpoint} - Status {status_code}: {error}")


# Global logger instance
logger = TeraaceLogger()