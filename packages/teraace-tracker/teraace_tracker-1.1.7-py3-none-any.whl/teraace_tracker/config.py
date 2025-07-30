"""
Configuration loader for Teraace tracker.
"""

import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration class for Teraace tracker."""
    
    def __init__(
        self, 
        env_file: Optional[str] = None,
        api_key: Optional[str] = None,
        buffer_size: Optional[int] = None,
        api_endpoint: Optional[str] = None,
        request_timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        org_id: Optional[str] = None
    ):
        """
        Initialize configuration from environment variables and direct arguments.
        
        Args:
            env_file: Path to .env file
            api_key: API key (overrides env var)
            buffer_size: Buffer size (overrides env var)
            api_endpoint: API endpoint (overrides env var)
            request_timeout: Request timeout (overrides env var)
            max_retries: Max retries (overrides env var)
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        # API key - direct argument takes precedence
        self.api_key = api_key or os.getenv("TERAACE_API_KEY")
        if not self.api_key:
            raise ValueError("TERAACE_API_KEY must be provided via environment variable or direct argument")
        
        # Buffer size with default 20, max 50 - direct argument takes precedence
        if buffer_size is not None:
            self.buffer_size = min(max(buffer_size, 1), 50)
        else:
            buffer_size_env = int(os.getenv("TERAACE_BUFFER_SIZE", "20"))
            self.buffer_size = min(max(buffer_size_env, 1), 50)
        
        # API endpoint - direct argument takes precedence
        self.api_endpoint = api_endpoint or os.getenv(
            "TERAACE_API_ENDPOINT", 
            "https://api.teraace.com/agent-events"
        )
        
        # Optional timeout settings - direct arguments take precedence
        self.request_timeout = request_timeout or int(os.getenv("TERAACE_REQUEST_TIMEOUT", "30"))
        self.max_retries = max_retries or int(os.getenv("TERAACE_MAX_RETRIES", "3"))
        
        # Organization ID - direct argument takes precedence
        self.org_id = org_id or os.getenv("TERAACE_ORG_ID")
    
    def __repr__(self):
        return (
            f"Config(buffer_size={self.buffer_size}, "
            f"api_endpoint='{self.api_endpoint}', "
            f"request_timeout={self.request_timeout}, "
            f"max_retries={self.max_retries})"
        )