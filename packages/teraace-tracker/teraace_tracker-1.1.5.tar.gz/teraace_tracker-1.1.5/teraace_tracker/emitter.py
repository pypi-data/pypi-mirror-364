"""
Framework-agnostic event emitter for Teraace tracker.
"""

import platform
import sys
from datetime import datetime, timezone
from typing import List, Optional
from .event_models import AgentEvent, ToolCall, MemoryEvent
from .buffer import EventBuffer
from .config import Config
from .logging_util import logger


class EventEmitter:
    """Framework-agnostic event emitter for tracking agent events."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize event emitter with configuration."""
        self.config = config or Config()
        self.buffer = EventBuffer(self.config)
        self._runtime = self._get_runtime_info()
        
        # Log initialization
        logger.info(f"🚀 Teraace Tracker: Initialized with endpoint {self.config.api_endpoint}")
        logger.info(f"📊 Teraace Tracker: Buffer size={self.config.buffer_size}, Runtime={self._runtime}")
    
    def _get_runtime_info(self) -> str:
        """Get runtime environment information."""
        python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
        system = platform.system().lower()
        return f"{python_version}/{system}"
    
    def emit_agent_event(
        self,
        agent_name: str,
        session_id: str,
        agent_framework: str,
        model: str,
        event_type: str,
        duration_ms: int,
        success: bool = True,
        exception: str = "",
        tool_calls: Optional[List[ToolCall]] = None,
        memory_events: Optional[List[MemoryEvent]] = None,
        run_env: str = "local",
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Emit an agent event to the buffer.
        
        Args:
            agent_name: Logical name/label for the agent
            session_id: Unique identifier per run/session
            agent_framework: Framework used ('langchain', 'crewai', 'autogpt')
            model: Model name (e.g., 'gpt-4o', 'claude-3')
            event_type: Event type ('start', 'end', 'error')
            duration_ms: Duration in milliseconds
            success: True if successful, False otherwise
            exception: Exception type/class if any
            tool_calls: List of tool calls
            memory_events: List of memory events
            run_env: Execution environment ('local', 'cloud', etc.)
            timestamp: Event timestamp (defaults to now)
        """
        event = AgentEvent(
            agent_name=agent_name,
            session_id=session_id,
            agent_framework=agent_framework,
            model=model,
            runtime=self._runtime,
            run_env=run_env,
            event_type=event_type,
            timestamp=timestamp or datetime.now(timezone.utc),
            duration_ms=duration_ms,
            success=success,
            exception=exception,
            tool_calls=tool_calls or [],
            memory_events=memory_events or []
        )
        
        logger.info(f"🎯 Teraace Tracker: Captured {event_type} event for agent '{agent_name}' (session: {session_id})")
        self.buffer.add_event(event)
    
    def create_tool_call(self, tool_name: str, timestamp: Optional[datetime] = None) -> ToolCall:
        """
        Create a ToolCall object.
        
        Args:
            tool_name: Name of the tool
            timestamp: When the tool was called (defaults to now)
            
        Returns:
            ToolCall object
        """
        return ToolCall(
            tool_name=tool_name,
            timestamp=timestamp or datetime.now(timezone.utc)
        )
    
    def create_memory_event(
        self, 
        event_type: str, 
        key: str, 
        timestamp: Optional[datetime] = None
    ) -> MemoryEvent:
        """
        Create a MemoryEvent object.
        
        Args:
            event_type: Type of memory operation ('read', 'write', 'update')
            key: Memory key that was accessed
            timestamp: When the operation occurred (defaults to now)
            
        Returns:
            MemoryEvent object
        """
        return MemoryEvent(
            event_type=event_type,
            key=key,
            timestamp=timestamp or datetime.now(timezone.utc)
        )
    
    async def flush_events(self) -> bool:
        """
        Manually flush all buffered events.
        
        Returns:
            bool: True if successful, False otherwise
        """
        return await self.buffer.flush()
    
    def get_buffer_size(self) -> int:
        """Get current buffer size."""
        return self.buffer.get_buffer_size()
    
    def emit_custom_event(
        self,
        agent_name: str,
        session_id: str,
        agent_framework: str,
        model: str,
        event_type: str,
        duration_ms: int,
        success: bool = True,
        exception: str = "",
        tool_calls: Optional[List[ToolCall]] = None,
        memory_events: Optional[List[MemoryEvent]] = None,
        run_env: str = "local",
        timestamp: Optional[datetime] = None,
        **custom_fields
    ) -> None:
        """
        Emit a custom agent event with additional flexibility.
        
        This method allows users to emit custom events with all the standard
        fields plus any additional custom metadata.
        
        Args:
            agent_name: Logical name/label for the agent
            session_id: Unique identifier per run/session
            agent_framework: Framework used ('custom', 'langchain', etc.)
            model: Model name (e.g., 'gpt-4o', 'claude-3')
            event_type: Event type ('start', 'end', 'error', or custom)
            duration_ms: Duration in milliseconds
            success: True if successful, False otherwise
            exception: Exception type/class if any
            tool_calls: List of tool calls
            memory_events: List of memory events
            run_env: Execution environment ('local', 'cloud', etc.)
            timestamp: Event timestamp (defaults to now)
            **custom_fields: Additional custom fields (logged but not sent to API)
        """
        if custom_fields:
            logger.debug(f"Custom event fields provided: {list(custom_fields.keys())}")
        
        self.emit_agent_event(
            agent_name=agent_name,
            session_id=session_id,
            agent_framework=agent_framework,
            model=model,
            event_type=event_type,
            duration_ms=duration_ms,
            success=success,
            exception=exception,
            tool_calls=tool_calls,
            memory_events=memory_events,
            run_env=run_env,
            timestamp=timestamp
        )