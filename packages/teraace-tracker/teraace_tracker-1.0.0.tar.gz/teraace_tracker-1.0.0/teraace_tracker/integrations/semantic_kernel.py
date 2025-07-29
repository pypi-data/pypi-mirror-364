"""
Semantic Kernel integration for Teraace tracker.
"""

import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Callable
from functools import wraps

from .base import BaseTracker, register_integration
from ..emitter import EventEmitter
from ..config import Config
from ..logging_util import logger


@register_integration("semantic_kernel")
class SemanticKernelTracker(BaseTracker):
    """Semantic Kernel integration for tracking agent events."""
    
    def __init__(
        self,
        agent_name: str,
        session_id: Optional[str] = None,
        config: Optional[Config] = None,
        run_env: str = "local"
    ):
        """
        Initialize Semantic Kernel tracker.
        
        Args:
            agent_name: Name of the agent being tracked
            session_id: Session identifier (auto-generated if not provided)
            config: Teraace configuration
            run_env: Runtime environment ('local', 'cloud', etc.)
        """
        super().__init__(agent_name, "semantic_kernel", session_id, config, run_env)
        
        logger.info(f"Semantic Kernel tracker initialized for agent '{agent_name}' session '{self.session_id}'")
    
    def extract_model_info(self, *args, **kwargs) -> str:
        """
        Extract model information from Semantic Kernel objects.
        
        Args:
            *args: Positional arguments that might contain model info
            **kwargs: Keyword arguments that might contain model info
            
        Returns:
            Model name or 'unknown'
        """
        # Try to extract from common Semantic Kernel patterns
        model_fields = ['model_id', 'model', 'service_id', 'ai_service']
        
        # Check kwargs first
        for field in model_fields:
            if field in kwargs and kwargs[field]:
                return str(kwargs[field])
        
        # Check positional arguments
        for arg in args:
            if hasattr(arg, 'model_id'):
                return str(arg.model_id)
            if hasattr(arg, 'service_id'):
                return str(arg.service_id)
            if hasattr(arg, 'ai_service') and hasattr(arg.ai_service, 'model_id'):
                return str(arg.ai_service.model_id)
        
        return "unknown"
    
    def create_kernel_execution_decorator(self, func):
        """
        Decorator to track Semantic Kernel execution.
        
        Args:
            func: Function to wrap and track
            
        Returns:
            Wrapped function with event tracking
        """
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            operation_id = str(uuid.uuid4())
            self.start_operation(operation_id)
            
            model = self.extract_model_info(*args, **kwargs)
            
            # Emit start event
            self.emit_lifecycle_event(
                event_type="start",
                duration_ms=0,
                model=model,
                success=True
            )
            
            try:
                result = await func(*args, **kwargs)
                
                duration_ms = self.end_operation(operation_id)
                tool_calls, memory_events = self.get_operation_data(operation_id)
                
                # Emit success event
                self.emit_lifecycle_event(
                    event_type="end",
                    duration_ms=duration_ms,
                    model=model,
                    success=True,
                    tool_calls=tool_calls,
                    memory_events=memory_events
                )
                
                return result
                
            except Exception as e:
                duration_ms = self.end_operation(operation_id)
                tool_calls, memory_events = self.get_operation_data(operation_id)
                
                # Emit error event
                self.emit_lifecycle_event(
                    event_type="error",
                    duration_ms=duration_ms,
                    model=model,
                    success=False,
                    exception=type(e).__name__,
                    tool_calls=tool_calls,
                    memory_events=memory_events
                )
                
                raise
            
            finally:
                self.cleanup_operation(operation_id)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            operation_id = str(uuid.uuid4())
            self.start_operation(operation_id)
            
            model = self.extract_model_info(*args, **kwargs)
            
            # Emit start event
            self.emit_lifecycle_event(
                event_type="start",
                duration_ms=0,
                model=model,
                success=True
            )
            
            try:
                result = func(*args, **kwargs)
                
                duration_ms = self.end_operation(operation_id)
                tool_calls, memory_events = self.get_operation_data(operation_id)
                
                # Emit success event
                self.emit_lifecycle_event(
                    event_type="end",
                    duration_ms=duration_ms,
                    model=model,
                    success=True,
                    tool_calls=tool_calls,
                    memory_events=memory_events
                )
                
                return result
                
            except Exception as e:
                duration_ms = self.end_operation(operation_id)
                tool_calls, memory_events = self.get_operation_data(operation_id)
                
                # Emit error event
                self.emit_lifecycle_event(
                    event_type="error",
                    duration_ms=duration_ms,
                    model=model,
                    success=False,
                    exception=type(e).__name__,
                    tool_calls=tool_calls,
                    memory_events=memory_events
                )
                
                raise
            
            finally:
                self.cleanup_operation(operation_id)
        
        # Return appropriate wrapper based on whether function is async
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    def track_skill_execution(self, skill_name: str, model: str = "unknown"):
        """
        Context manager for tracking Semantic Kernel skill execution.
        
        Args:
            skill_name: Name of the skill being executed
            model: Model being used for the skill
            
        Returns:
            Context manager for skill tracking
        """
        return SkillExecutionContext(self, skill_name, model)
    
    def track_planner_execution(self, planner_name: str, model: str = "unknown"):
        """
        Context manager for tracking Semantic Kernel planner execution.
        
        Args:
            planner_name: Name of the planner being executed
            model: Model being used for the planner
            
        Returns:
            Context manager for planner tracking
        """
        return PlannerExecutionContext(self, planner_name, model)
    
    def log_skill_call(self, skill_name: str, operation_id: Optional[str] = None):
        """
        Log a skill call event.
        
        Args:
            skill_name: Name of the skill being called
            operation_id: Operation ID to associate with (optional)
        """
        self.log_tool_call(f"skill:{skill_name}", operation_id)
    
    def log_connector_call(self, connector_name: str, operation_id: Optional[str] = None):
        """
        Log a connector call event.
        
        Args:
            connector_name: Name of the connector being called
            operation_id: Operation ID to associate with (optional)
        """
        self.log_tool_call(f"connector:{connector_name}", operation_id)
    
    def _emit_event(self, event_type: str, data: Dict[str, Any], timestamp: Optional[datetime] = None):
        """
        Emit a custom event with the given type and data.
        
        Args:
            event_type: Type of the event
            data: Event data dictionary
            timestamp: Optional timestamp for the event
        """
        # Create a basic agent event with the custom data
        self.emitter.emit_agent_event(
            agent_name=self.agent_name,
            session_id=self.session_id,
            agent_framework=self.framework_name,
            model=data.get('model', 'unknown'),
            event_type=event_type,
            duration_ms=data.get('duration_ms', 0),
            success=data.get('success', True),
            exception=data.get('exception', ''),
            tool_calls=[],
            memory_events=[],
            run_env=self.run_env,
            timestamp=timestamp
        )
    
    def track_kernel_execution(self, kernel, function, variables: Dict[str, Any]):
        """
        Track kernel execution event.
        
        Args:
            kernel: Semantic Kernel instance
            function: Function being executed
            variables: Input variables
        """
        function_name = getattr(function, 'name', str(function))
        skill_name = getattr(function, 'skill_name', 'unknown')
        
        self._emit_event(
            event_type='kernel_execution_start',
            data={
                'function_name': function_name,
                'skill_name': skill_name,
                'model': self.extract_model_info(kernel, function)
            }
        )
    
    def track_planner_operation(self, planner, operation: str, data: Dict[str, Any]):
        """
        Track planner operation event.
        
        Args:
            planner: Planner object
            operation: Operation being performed
            data: Operation data
        """
        self._emit_event(
            event_type='planner_operation',
            data={
                'planner_type': planner.__class__.__name__,
                'operation': operation,
                'model': self.extract_model_info(planner)
            }
        )
    
    def track_memory_operation(self, memory, operation: str, data: Dict[str, Any]):
        """
        Track memory operation event.
        
        Args:
            memory: Memory store object
            operation: Operation being performed
            data: Operation data
        """
        self._emit_event(
            event_type='memory_operation',
            data={
                'memory_type': memory.__class__.__name__,
                'operation': operation,
                'model': self.extract_model_info(memory)
            }
        )
    
    def track_connector_call(self, connector, method: str, data: Dict[str, Any]):
        """
        Track connector call event.
        
        Args:
            connector: Connector object
            method: Method being called
            data: Call data
        """
        self._emit_event(
            event_type='connector_call',
            data={
                'connector_type': connector.__class__.__name__,
                'method': method,
                'model': self.extract_model_info(connector)
            }
        )
    
    def auto_track_kernel(self, kernel):
        """
        Automatically track a Semantic Kernel instance.
        
        Args:
            kernel: Semantic Kernel instance to track
            
        Returns:
            The kernel object (for chaining)
        """
        self._tracked_kernel = kernel
        return kernel


class SkillExecutionContext:
    """Context manager for tracking Semantic Kernel skill execution."""
    
    def __init__(self, tracker: SemanticKernelTracker, skill_name: str, model: str):
        """
        Initialize skill execution context.
        
        Args:
            tracker: Semantic Kernel tracker instance
            skill_name: Name of the skill
            model: Model being used
        """
        self.tracker = tracker
        self.skill_name = skill_name
        self.model = model
        self.operation_id = str(uuid.uuid4())
    
    def __enter__(self):
        """Enter the context manager."""
        self.tracker.start_operation(self.operation_id)
        
        # Emit start event
        self.tracker.emit_lifecycle_event(
            event_type="start",
            duration_ms=0,
            model=self.model,
            success=True,
            agent_name_suffix=f"skill:{self.skill_name}"
        )
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        duration_ms = self.tracker.end_operation(self.operation_id)
        tool_calls, memory_events = self.tracker.get_operation_data(self.operation_id)
        
        if exc_type is None:
            # Success
            self.tracker.emit_lifecycle_event(
                event_type="end",
                duration_ms=duration_ms,
                model=self.model,
                success=True,
                tool_calls=tool_calls,
                memory_events=memory_events,
                agent_name_suffix=f"skill:{self.skill_name}"
            )
        else:
            # Error
            self.tracker.emit_lifecycle_event(
                event_type="error",
                duration_ms=duration_ms,
                model=self.model,
                success=False,
                exception=exc_type.__name__ if exc_type else "",
                tool_calls=tool_calls,
                memory_events=memory_events,
                agent_name_suffix=f"skill:{self.skill_name}"
            )
        
        # Clean up
        self.tracker.cleanup_operation(self.operation_id)
    
    def log_skill_call(self, skill_name: str):
        """Log a skill call within this context."""
        self.tracker.log_skill_call(skill_name, self.operation_id)
    
    def log_connector_call(self, connector_name: str):
        """Log a connector call within this context."""
        self.tracker.log_connector_call(connector_name, self.operation_id)
    
    def log_memory_event(self, event_type: str, key: str):
        """Log a memory event within this context."""
        self.tracker.log_memory_event(event_type, key, self.operation_id)


class PlannerExecutionContext:
    """Context manager for tracking Semantic Kernel planner execution."""
    
    def __init__(self, tracker: SemanticKernelTracker, planner_name: str, model: str):
        """
        Initialize planner execution context.
        
        Args:
            tracker: Semantic Kernel tracker instance
            planner_name: Name of the planner
            model: Model being used
        """
        self.tracker = tracker
        self.planner_name = planner_name
        self.model = model
        self.operation_id = str(uuid.uuid4())
    
    def __enter__(self):
        """Enter the context manager."""
        self.tracker.start_operation(self.operation_id)
        
        # Emit start event
        self.tracker.emit_lifecycle_event(
            event_type="start",
            duration_ms=0,
            model=self.model,
            success=True,
            agent_name_suffix=f"planner:{self.planner_name}"
        )
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        duration_ms = self.tracker.end_operation(self.operation_id)
        tool_calls, memory_events = self.tracker.get_operation_data(self.operation_id)
        
        if exc_type is None:
            # Success
            self.tracker.emit_lifecycle_event(
                event_type="end",
                duration_ms=duration_ms,
                model=self.model,
                success=True,
                tool_calls=tool_calls,
                memory_events=memory_events,
                agent_name_suffix=f"planner:{self.planner_name}"
            )
        else:
            # Error
            self.tracker.emit_lifecycle_event(
                event_type="error",
                duration_ms=duration_ms,
                model=self.model,
                success=False,
                exception=exc_type.__name__ if exc_type else "",
                tool_calls=tool_calls,
                memory_events=memory_events,
                agent_name_suffix=f"planner:{self.planner_name}"
            )
        
        # Clean up
        self.tracker.cleanup_operation(self.operation_id)
    
    def log_skill_call(self, skill_name: str):
        """Log a skill call within this planner context."""
        self.tracker.log_skill_call(skill_name, self.operation_id)
    
    def log_memory_event(self, event_type: str, key: str):
        """Log a memory event within this planner context."""
        self.tracker.log_memory_event(event_type, key, self.operation_id)


