"""
CrewAI integration for Teraace tracker.
"""

import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from functools import wraps

from ..emitter import EventEmitter
from ..config import Config
from ..logging_util import logger


class CrewAITracker:
    """CrewAI integration for tracking agent and task events."""
    
    def __init__(
        self,
        agent_name: str,
        session_id: Optional[str] = None,
        config: Optional[Config] = None,
        run_env: str = "local"
    ):
        """
        Initialize CrewAI tracker.
        
        Args:
            agent_name: Name of the agent being tracked
            session_id: Session identifier (auto-generated if not provided)
            config: Teraace configuration
            run_env: Runtime environment ('local', 'cloud', etc.)
        """
        self.agent_name = agent_name
        self.session_id = session_id or str(uuid.uuid4())
        self.run_env = run_env
        self.emitter = EventEmitter(config)
        
        # Track ongoing operations
        self._task_start_times: Dict[str, float] = {}
        self._tool_calls: Dict[str, List] = {}
        self._memory_events: Dict[str, List] = {}
        
        logger.info(f"CrewAI tracker initialized for agent '{agent_name}' session '{self.session_id}'")
    
    def track_agent_execution(self, func):
        """
        Decorator to track agent execution lifecycle.
        
        Args:
            func: Function to wrap and track
            
        Returns:
            Wrapped function with event tracking
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            execution_id = str(uuid.uuid4())
            start_time = time.time()
            
            # Initialize tracking for this execution
            self._task_start_times[execution_id] = start_time
            self._tool_calls[execution_id] = []
            self._memory_events[execution_id] = []
            
            # Extract model information from args/kwargs
            model = self._extract_model_info(args, kwargs)
            
            # Emit start event
            self.emitter.emit_agent_event(
                agent_name=self.agent_name,
                session_id=self.session_id,
                agent_framework="crewai",
                model=model,
                event_type="start",
                duration_ms=0,
                success=True,
                run_env=self.run_env
            )
            
            try:
                # Execute the original function
                result = func(*args, **kwargs)
                
                # Calculate duration
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Emit success event
                self.emitter.emit_agent_event(
                    agent_name=self.agent_name,
                    session_id=self.session_id,
                    agent_framework="crewai",
                    model=model,
                    event_type="end",
                    duration_ms=duration_ms,
                    success=True,
                    tool_calls=self._tool_calls.get(execution_id, []),
                    memory_events=self._memory_events.get(execution_id, []),
                    run_env=self.run_env
                )
                
                return result
                
            except Exception as e:
                # Calculate duration
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Emit error event
                self.emitter.emit_agent_event(
                    agent_name=self.agent_name,
                    session_id=self.session_id,
                    agent_framework="crewai",
                    model=model,
                    event_type="error",
                    duration_ms=duration_ms,
                    success=False,
                    exception=type(e).__name__,
                    tool_calls=self._tool_calls.get(execution_id, []),
                    memory_events=self._memory_events.get(execution_id, []),
                    run_env=self.run_env
                )
                
                raise
            
            finally:
                # Clean up tracking data
                self._cleanup_execution_data(execution_id)
        
        return wrapper
    
    def track_task_execution(self, task_name: str, model: str = "unknown"):
        """
        Context manager for tracking task execution.
        
        Args:
            task_name: Name of the task being executed
            model: Model being used for the task
            
        Returns:
            Context manager for task tracking
        """
        return TaskExecutionContext(self, task_name, model)
    
    def log_tool_call(self, tool_name: str, execution_id: Optional[str] = None):
        """
        Log a tool call event.
        
        Args:
            tool_name: Name of the tool being called
            execution_id: Execution ID to associate with (optional)
        """
        tool_call = self.emitter.create_tool_call(tool_name)
        
        if execution_id and execution_id in self._tool_calls:
            self._tool_calls[execution_id].append(tool_call)
        
        logger.debug(f"Tool '{tool_name}' called for agent {self.agent_name}")
    
    def log_memory_event(self, event_type: str, key: str, execution_id: Optional[str] = None):
        """
        Log a memory operation event.
        
        Args:
            event_type: Type of memory operation ('read', 'write', 'update')
            key: Memory key being accessed
            execution_id: Execution ID to associate with (optional)
        """
        memory_event = self.emitter.create_memory_event(event_type, key)
        
        if execution_id and execution_id in self._memory_events:
            self._memory_events[execution_id].append(memory_event)
        
        logger.debug(f"Memory {event_type} on key '{key}' for agent {self.agent_name}")
    
    def _extract_model_info(self, args: tuple, kwargs: dict) -> str:
        """
        Extract model information from function arguments.
        
        Args:
            args: Function positional arguments
            kwargs: Function keyword arguments
            
        Returns:
            Model name or 'unknown'
        """
        # Try to extract model from common CrewAI patterns
        if 'model' in kwargs:
            return str(kwargs['model'])
        
        if 'llm' in kwargs and hasattr(kwargs['llm'], 'model_name'):
            return kwargs['llm'].model_name
        
        # Check for agent objects with model info
        for arg in args:
            if hasattr(arg, 'llm') and hasattr(arg.llm, 'model_name'):
                return arg.llm.model_name
            if hasattr(arg, 'model'):
                return str(arg.model)
        
        return "unknown"
    
    def _cleanup_execution_data(self, execution_id: str):
        """Clean up tracking data for completed execution."""
        self._task_start_times.pop(execution_id, None)
        self._tool_calls.pop(execution_id, None)
        self._memory_events.pop(execution_id, None)
    
    async def flush_events(self) -> bool:
        """Manually flush all buffered events."""
        return await self.emitter.flush_events()
    
    def get_buffer_size(self) -> int:
        """Get current buffer size."""
        return self.emitter.get_buffer_size()


class TaskExecutionContext:
    """Context manager for tracking CrewAI task execution."""
    
    def __init__(self, tracker: CrewAITracker, task_name: str, model: str):
        """
        Initialize task execution context.
        
        Args:
            tracker: CrewAI tracker instance
            task_name: Name of the task
            model: Model being used
        """
        self.tracker = tracker
        self.task_name = task_name
        self.model = model
        self.execution_id = str(uuid.uuid4())
        self.start_time = None
    
    def __enter__(self):
        """Enter the context manager."""
        self.start_time = time.time()
        
        # Initialize tracking
        self.tracker._task_start_times[self.execution_id] = self.start_time
        self.tracker._tool_calls[self.execution_id] = []
        self.tracker._memory_events[self.execution_id] = []
        
        # Emit start event
        self.tracker.emitter.emit_agent_event(
            agent_name=f"{self.tracker.agent_name}:{self.task_name}",
            session_id=self.tracker.session_id,
            agent_framework="crewai",
            model=self.model,
            event_type="start",
            duration_ms=0,
            success=True,
            run_env=self.tracker.run_env
        )
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        duration_ms = int((time.time() - self.start_time) * 1000)
        
        if exc_type is None:
            # Success
            self.tracker.emitter.emit_agent_event(
                agent_name=f"{self.tracker.agent_name}:{self.task_name}",
                session_id=self.tracker.session_id,
                agent_framework="crewai",
                model=self.model,
                event_type="end",
                duration_ms=duration_ms,
                success=True,
                tool_calls=self.tracker._tool_calls.get(self.execution_id, []),
                memory_events=self.tracker._memory_events.get(self.execution_id, []),
                run_env=self.tracker.run_env
            )
        else:
            # Error
            self.tracker.emitter.emit_agent_event(
                agent_name=f"{self.tracker.agent_name}:{self.task_name}",
                session_id=self.tracker.session_id,
                agent_framework="crewai",
                model=self.model,
                event_type="error",
                duration_ms=duration_ms,
                success=False,
                exception=exc_type.__name__ if exc_type else "",
                tool_calls=self.tracker._tool_calls.get(self.execution_id, []),
                memory_events=self.tracker._memory_events.get(self.execution_id, []),
                run_env=self.tracker.run_env
            )
        
        # Clean up
        self.tracker._cleanup_execution_data(self.execution_id)
    
    def log_tool_call(self, tool_name: str):
        """Log a tool call within this task context."""
        self.tracker.log_tool_call(tool_name, self.execution_id)
    
    def log_memory_event(self, event_type: str, key: str):
        """Log a memory event within this task context."""
        self.tracker.log_memory_event(event_type, key, self.execution_id)