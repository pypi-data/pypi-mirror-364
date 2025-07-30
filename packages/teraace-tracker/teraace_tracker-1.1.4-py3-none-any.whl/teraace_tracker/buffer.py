"""
Event buffer for batching and flushing events to API.
"""

import asyncio
from typing import List, Optional
from threading import Lock
from .event_models import AgentEvent
from .client import TeraaceAPIClient
from .config import Config
from .logging_util import logger


class EventBuffer:
    """Thread-safe event buffer with automatic and manual flush capabilities."""
    
    def __init__(self, config: Config):
        """Initialize event buffer with configuration."""
        self.config = config
        self.events: List[AgentEvent] = []
        self.lock = Lock()
        self._client: Optional[TeraaceAPIClient] = None
    
    def add_event(self, event: AgentEvent) -> None:
        """
        Add event to buffer and trigger flush if buffer is full.
        
        Args:
            event: AgentEvent to add to buffer
        """
        with self.lock:
            # Check for buffer overflow
            if len(self.events) >= self.config.buffer_size * 2:
                # Drop oldest events to prevent memory issues
                dropped_count = len(self.events) - self.config.buffer_size + 1
                self.events = self.events[dropped_count:]
                logger.warning(f"Buffer overflow: dropped {dropped_count} oldest events")
            
            self.events.append(event)
            logger.info(f"📦 Teraace Buffer: Added event, buffer now has {len(self.events)}/{self.config.buffer_size} events")
            
            # Auto-flush when buffer is full
            if len(self.events) >= self.config.buffer_size:
                logger.info(f"🚨 Teraace Buffer: Buffer full ({len(self.events)} events), triggering auto-flush")
                try:
                    asyncio.create_task(self._flush_async())
                except RuntimeError:
                    # No event loop running, skip auto-flush
                    logger.warning("⚠️ Teraace Buffer: No event loop running, skipping auto-flush")
    
    async def flush(self) -> bool:
        """
        Manually flush all events in buffer to API.
        
        Returns:
            bool: True if successful, False otherwise
        """
        return await self._flush_async()
    
    async def _flush_async(self) -> bool:
        """Internal async flush implementation."""
        events_to_send = []
        
        with self.lock:
            if not self.events:
                return True
            
            events_to_send = self.events.copy()
            self.events.clear()
        
        logger.log_flush_attempt(len(events_to_send))
        
        try:
            async with TeraaceAPIClient(self.config) as client:
                success = await client.send_events(events_to_send)
                
                if success:
                    logger.log_flush_success(len(events_to_send))
                    return True
                else:
                    # Put events back in buffer on failure
                    with self.lock:
                        self.events.extend(events_to_send)
                    logger.log_flush_error(len(events_to_send), "API request failed")
                    return False
                    
        except Exception as e:
            # Put events back in buffer on exception
            with self.lock:
                self.events.extend(events_to_send)
            logger.log_flush_error(len(events_to_send), str(e))
            return False
    
    def get_buffer_size(self) -> int:
        """Get current number of events in buffer."""
        with self.lock:
            return len(self.events)
    
    def clear_buffer(self) -> None:
        """Clear all events from buffer (for testing/cleanup)."""
        with self.lock:
            self.events.clear()
            logger.debug("Buffer cleared")