"""
Async API client for Teraace API.
"""

import asyncio
import aiohttp
import json
from typing import List, Dict, Any
from .event_models import AgentEvent
from .config import Config
from .logging_util import logger


class TeraaceAPIClient:
    """Async HTTP client for Teraace API."""
    
    def __init__(self, config: Config):
        """Initialize API client with configuration."""
        self.config = config
        self.session: aiohttp.ClientSession = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.request_timeout),
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def send_events(self, events: List[AgentEvent]) -> bool:
        """
        Send events to Teraace API with retry logic.
        
        Args:
            events: List of AgentEvent objects to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not events:
            return True
        
        # Convert events to JSON
        payload = {
            "events": [event.model_dump(mode="json") for event in events]
        }
        
        for attempt in range(self.config.max_retries):
            logger.log_api_attempt(self.config.api_endpoint, len(events), attempt + 1, self.config.max_retries)
            
            try:
                async with self.session.post(
                    self.config.api_endpoint,
                    json=payload
                ) as response:
                    logger.log_api_call(self.config.api_endpoint, response.status)
                    
                    if response.status == 200 or response.status == 201:
                        logger.log_api_success(self.config.api_endpoint, len(events))
                        return True
                    elif response.status >= 400 and response.status < 500:
                        # Client error - don't retry
                        error_text = await response.text()
                        logger.log_api_error(self.config.api_endpoint, len(events), response.status, error_text)
                        return False
                    else:
                        # Server error - retry
                        error_text = await response.text()
                        logger.log_api_error(self.config.api_endpoint, len(events), response.status, error_text)
                        if attempt == self.config.max_retries - 1:
                            logger.error(f"❌ Teraace API: Giving up after {self.config.max_retries} attempts")
                        
            except asyncio.TimeoutError:
                logger.warning(f"Request timeout (attempt {attempt + 1})")
            except aiohttp.ClientError as e:
                logger.warning(f"Client error (attempt {attempt + 1}): {e}")
            except Exception as e:
                logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")
            
            # Exponential backoff
            if attempt < self.config.max_retries - 1:
                wait_time = 2 ** attempt
                logger.debug(f"Waiting {wait_time}s before retry")
                await asyncio.sleep(wait_time)
        
        logger.error(f"Failed to send events after {self.config.max_retries} attempts")
        return False