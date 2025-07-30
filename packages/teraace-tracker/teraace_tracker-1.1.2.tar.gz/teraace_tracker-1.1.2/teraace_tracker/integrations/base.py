"""
Base classes and framework for creating new integrations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import uuid
import time
from datetime import datetime

from ..emitter import EventEmitter
from ..config import Config
from ..logging_util import logger


class BaseTracker(ABC):
    """
    Base class for all framework integrations.
    
    This provides a template and common functionality for creating
    new integrations with different AI agent frameworks.
    """
    
    def __init__(
        self,
        agent_name: str,
        framework_name: str,
        session_id: Optional[str] = None,
        config: Optional[Config] = None,
        run_env: str = "local"
    ):
        """
        Initialize base tracker.
        
        Args:
            agent_name: Name of the agent being tracked
            framework_name: Name of the framework ('langchain', 'crewai', etc.)
            session_id: Session identifier (auto-generated if not provided)
            config: Teraace configuration
            run_env: Runtime environment ('local', 'cloud', etc.)
        """
        self.agent_name = agent_name
        self.framework_name = framework_name
        self.session_id = session_id or str(uuid.uuid4())
        self.run_env = run_env
        self.emitter = EventEmitter(config)
        
        # Track ongoing operations
        self._operation_start_times: Dict[str, float] = {}
        self._tool_calls: Dict[str, List] = {}
        self._memory_events: Dict[str, List] = {}
        
        logger.info(f"{framework_name.title()} tracker initialized for agent '{agent_name}' session '{self.session_id}'")
    
    @abstractmethod
    def extract_model_info(self, *args, **kwargs) -> str:
        """
        Extract model information from framework-specific objects.
        
        This method should be implemented by each integration to handle
        the specific way that framework stores model information.
        
        Returns:
            Model name or 'unknown'
        """
        pass
    
    def emit_lifecycle_event(
        self,
        event_type: str,
        duration_ms: int,
        model: str,
        success: bool = True,
        exception: str = "",
        tool_calls: Optional[List] = None,
        memory_events: Optional[List] = None,
        agent_name_suffix: str = ""
    ) -> None:
        """
        Emit an agent lifecycle event.
        
        Args:
            event_type: Type of event ('start', 'end', 'error')
            duration_ms: Duration in milliseconds
            model: Model being used
            success: Whether the operation was successful
            exception: Exception type if any
            tool_calls: List of tool calls
            memory_events: List of memory events
            agent_name_suffix: Optional suffix for agent name
        """
        full_agent_name = f"{self.agent_name}:{agent_name_suffix}" if agent_name_suffix else self.agent_name
        
        self.emitter.emit_agent_event(
            agent_name=full_agent_name,
            session_id=self.session_id,
            agent_framework=self.framework_name,
            model=model,
            event_type=event_type,
            duration_ms=duration_ms,
            success=success,
            exception=exception,
            tool_calls=tool_calls or [],
            memory_events=memory_events or [],
            run_env=self.run_env
        )
    
    def start_operation(self, operation_id: str) -> None:
        """Start tracking an operation."""
        self._operation_start_times[operation_id] = time.time()
        self._tool_calls[operation_id] = []
        self._memory_events[operation_id] = []
    
    def end_operation(self, operation_id: str) -> int:
        """End tracking an operation and return duration."""
        start_time = self._operation_start_times.get(operation_id, time.time())
        duration_ms = int((time.time() - start_time) * 1000)
        return duration_ms
    
    def cleanup_operation(self, operation_id: str) -> None:
        """Clean up tracking data for an operation."""
        self._operation_start_times.pop(operation_id, None)
        self._tool_calls.pop(operation_id, None)
        self._memory_events.pop(operation_id, None)
    
    def log_tool_call(self, tool_name: str, operation_id: Optional[str] = None) -> None:
        """Log a tool call for an operation."""
        tool_call = self.emitter.create_tool_call(tool_name)
        
        if operation_id and operation_id in self._tool_calls:
            self._tool_calls[operation_id].append(tool_call)
        
        logger.debug(f"Tool '{tool_name}' called for {self.framework_name} agent {self.agent_name}")
    
    def log_memory_event(self, event_type: str, key: str, operation_id: Optional[str] = None) -> None:
        """Log a memory event for an operation."""
        memory_event = self.emitter.create_memory_event(event_type, key)
        
        if operation_id and operation_id in self._memory_events:
            self._memory_events[operation_id].append(memory_event)
        
        logger.debug(f"Memory {event_type} on key '{key}' for {self.framework_name} agent {self.agent_name}")
    
    def get_operation_data(self, operation_id: str) -> tuple:
        """Get tool calls and memory events for an operation."""
        tool_calls = self._tool_calls.get(operation_id, [])
        memory_events = self._memory_events.get(operation_id, [])
        return tool_calls, memory_events
    
    async def flush_events(self) -> bool:
        """Manually flush all buffered events."""
        return await self.emitter.flush_events()
    
    def get_buffer_size(self) -> int:
        """Get current buffer size."""
        return self.emitter.get_buffer_size()


class IntegrationRegistry:
    """Registry for managing available integrations."""
    
    _integrations: Dict[str, type] = {}
    
    @classmethod
    def register(cls, framework_name: str, tracker_class: type) -> None:
        """Register a new integration."""
        cls._integrations[framework_name] = tracker_class
        logger.info(f"Registered integration for {framework_name}")
    
    @classmethod
    def get_integration(cls, framework_name: str) -> Optional[type]:
        """Get an integration by framework name."""
        return cls._integrations.get(framework_name)
    
    @classmethod
    def list_integrations(cls) -> List[str]:
        """List all registered integrations."""
        return list(cls._integrations.keys())
    
    @classmethod
    def create_tracker(cls, framework_name: str, *args, **kwargs) -> Optional[BaseTracker]:
        """Create a tracker instance for a framework."""
        tracker_class = cls.get_integration(framework_name)
        if tracker_class:
            return tracker_class(*args, **kwargs)
        return None


def register_integration(framework_name: str):
    """Decorator for registering integrations."""
    def decorator(tracker_class):
        IntegrationRegistry.register(framework_name, tracker_class)
        return tracker_class
    return decorator