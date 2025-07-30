"""
Graceful shutdown handler for flushing events on exit.
"""

import atexit
import signal
import asyncio
from typing import Optional
from .emitter import EventEmitter
from .logging_util import logger


class ShutdownHandler:
    """Handles graceful shutdown and event flushing."""
    
    def __init__(self, emitter: EventEmitter):
        """Initialize shutdown handler with event emitter."""
        self.emitter = emitter
        self._registered = False
    
    def register(self) -> None:
        """Register shutdown handlers for various exit scenarios."""
        if self._registered:
            return
        
        # Register atexit handler
        atexit.register(self._sync_shutdown)
        
        # Register signal handlers for common termination signals
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # On Windows, also handle SIGBREAK
        if hasattr(signal, 'SIGBREAK'):
            signal.signal(signal.SIGBREAK, self._signal_handler)
        
        self._registered = True
        logger.debug("Shutdown handlers registered")
    
    def _signal_handler(self, signum: int, frame) -> None:
        """Handle termination signals."""
        logger.info(f"Received signal {signum}, flushing events before exit")
        self._sync_shutdown()
    
    def _sync_shutdown(self) -> None:
        """Synchronous shutdown handler that flushes events."""
        try:
            # Get or create event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Flush events
            buffer_size = self.emitter.get_buffer_size()
            if buffer_size > 0:
                logger.info(f"Flushing {buffer_size} events on shutdown")
                success = loop.run_until_complete(self.emitter.flush_events())
                if success:
                    logger.info("Successfully flushed events on shutdown")
                else:
                    logger.error("Failed to flush events on shutdown")
            else:
                logger.debug("No events to flush on shutdown")
                
        except Exception as e:
            logger.error(f"Error during shutdown flush: {e}")
        finally:
            try:
                loop.close()
            except:
                pass


def setup_graceful_shutdown(emitter: EventEmitter) -> ShutdownHandler:
    """
    Set up graceful shutdown handling for an event emitter.
    
    Args:
        emitter: EventEmitter instance to flush on shutdown
        
    Returns:
        ShutdownHandler instance
    """
    handler = ShutdownHandler(emitter)
    handler.register()
    return handler