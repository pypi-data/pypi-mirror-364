"""
AutoGPT integration for Teraace tracker.
"""

import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Callable
from functools import wraps

from ..emitter import EventEmitter
from ..config import Config
from ..logging_util import logger


class AutoGPTTracker:
    """AutoGPT integration for tracking agent events."""
    
    def __init__(
        self,
        agent_name: str,
        session_id: Optional[str] = None,
        config: Optional[Config] = None,
        run_env: str = "local"
    ):
        """
        Initialize AutoGPT tracker.
        
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
        self._execution_start_times: Dict[str, float] = {}
        self._tool_calls: Dict[str, List] = {}
        self._memory_events: Dict[str, List] = {}
        
        logger.info(f"AutoGPT tracker initialized for agent '{agent_name}' session '{self.session_id}'")
    
    def patch_agent_loop(self, agent_instance):
        """
        Patch an AutoGPT agent instance to track its execution loop.
        
        Args:
            agent_instance: AutoGPT agent instance to patch
            
        Returns:
            Patched agent instance
        """
        # Store original methods
        original_run = getattr(agent_instance, 'run', None)
        original_execute_command = getattr(agent_instance, 'execute_command', None)
        original_think = getattr(agent_instance, 'think', None)
        
        # Patch run method
        if original_run:
            agent_instance.run = self._wrap_agent_run(original_run, agent_instance)
        
        # Patch execute_command method
        if original_execute_command:
            agent_instance.execute_command = self._wrap_execute_command(original_execute_command, agent_instance)
        
        # Patch think method
        if original_think:
            agent_instance.think = self._wrap_think_method(original_think, agent_instance)
        
        logger.info(f"AutoGPT agent '{self.agent_name}' patched for tracking")
        return agent_instance
    
    def _wrap_agent_run(self, original_run: Callable, agent_instance) -> Callable:
        """Wrap the agent's main run method."""
        @wraps(original_run)
        def wrapper(*args, **kwargs):
            execution_id = str(uuid.uuid4())
            start_time = time.time()
            
            # Initialize tracking
            self._execution_start_times[execution_id] = start_time
            self._tool_calls[execution_id] = []
            self._memory_events[execution_id] = []
            
            # Extract model information
            model = self._extract_model_info(agent_instance)
            
            # Emit start event
            self.emitter.emit_agent_event(
                agent_name=self.agent_name,
                session_id=self.session_id,
                agent_framework="autogpt",
                model=model,
                event_type="start",
                duration_ms=0,
                success=True,
                run_env=self.run_env
            )
            
            try:
                # Execute original method
                result = original_run(*args, **kwargs)
                
                # Calculate duration
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Emit success event
                self.emitter.emit_agent_event(
                    agent_name=self.agent_name,
                    session_id=self.session_id,
                    agent_framework="autogpt",
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
                    agent_framework="autogpt",
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
                # Clean up
                self._cleanup_execution_data(execution_id)
        
        return wrapper
    
    def _wrap_execute_command(self, original_execute: Callable, agent_instance) -> Callable:
        """Wrap the agent's command execution method."""
        @wraps(original_execute)
        def wrapper(command_name: str, *args, **kwargs):
            # Log tool call
            self.log_tool_call(command_name)
            
            # Execute original method
            return original_execute(command_name, *args, **kwargs)
        
        return wrapper
    
    def _wrap_think_method(self, original_think: Callable, agent_instance) -> Callable:
        """Wrap the agent's thinking/planning method."""
        @wraps(original_think)
        def wrapper(*args, **kwargs):
            # Log memory read event (thinking involves reading context)
            self.log_memory_event("read", "agent_context")
            
            # Execute original method
            result = original_think(*args, **kwargs)
            
            # Log memory write event (thinking produces new thoughts)
            self.log_memory_event("write", "agent_thoughts")
            
            return result
        
        return wrapper
    
    def track_command_execution(self, command_name: str, model: str = "unknown"):
        """
        Context manager for tracking individual command execution.
        
        Args:
            command_name: Name of the command being executed
            model: Model being used for the command
            
        Returns:
            Context manager for command tracking
        """
        return CommandExecutionContext(self, command_name, model)
    
    def log_tool_call(self, tool_name: str, execution_id: Optional[str] = None):
        """
        Log a tool/command call event.
        
        Args:
            tool_name: Name of the tool/command being called
            execution_id: Execution ID to associate with (optional)
        """
        tool_call = self.emitter.create_tool_call(tool_name)
        
        # If no specific execution_id, add to the most recent one
        if execution_id is None and self._tool_calls:
            execution_id = list(self._tool_calls.keys())[-1]
        
        if execution_id and execution_id in self._tool_calls:
            self._tool_calls[execution_id].append(tool_call)
        
        logger.debug(f"Command '{tool_name}' executed for agent {self.agent_name}")
    
    def log_memory_event(self, event_type: str, key: str, execution_id: Optional[str] = None):
        """
        Log a memory operation event.
        
        Args:
            event_type: Type of memory operation ('read', 'write', 'update')
            key: Memory key being accessed
            execution_id: Execution ID to associate with (optional)
        """
        memory_event = self.emitter.create_memory_event(event_type, key)
        
        # If no specific execution_id, add to the most recent one
        if execution_id is None and self._memory_events:
            execution_id = list(self._memory_events.keys())[-1]
        
        if execution_id and execution_id in self._memory_events:
            self._memory_events[execution_id].append(memory_event)
        
        logger.debug(f"Memory {event_type} on key '{key}' for agent {self.agent_name}")
    
    def _extract_model_info(self, agent_instance) -> str:
        """
        Extract model information from AutoGPT agent instance.
        
        Args:
            agent_instance: AutoGPT agent instance
            
        Returns:
            Model name or 'unknown'
        """
        # Try common AutoGPT model attribute patterns
        model_attrs = ['model', 'model_name', 'llm_model', 'gpt_model']
        
        for attr in model_attrs:
            if hasattr(agent_instance, attr):
                model_value = getattr(agent_instance, attr)
                if model_value and str(model_value) != "None":
                    return str(model_value)
        
        # Check for nested LLM objects
        if hasattr(agent_instance, 'llm'):
            llm = agent_instance.llm
            for attr in model_attrs:
                if hasattr(llm, attr):
                    model_value = getattr(llm, attr)
                    if model_value:
                        return str(model_value)
        
        # Check for config objects
        if hasattr(agent_instance, 'config'):
            config = agent_instance.config
            for attr in model_attrs:
                if hasattr(config, attr):
                    model_value = getattr(config, attr)
                    if model_value:
                        return str(model_value)
        
        return "unknown"
    
    def _cleanup_execution_data(self, execution_id: str):
        """Clean up tracking data for completed execution."""
        self._execution_start_times.pop(execution_id, None)
        self._tool_calls.pop(execution_id, None)
        self._memory_events.pop(execution_id, None)
    
    async def flush_events(self) -> bool:
        """Manually flush all buffered events."""
        return await self.emitter.flush_events()
    
    def get_buffer_size(self) -> int:
        """Get current buffer size."""
        return self.emitter.get_buffer_size()


class CommandExecutionContext:
    """Context manager for tracking AutoGPT command execution."""
    
    def __init__(self, tracker: AutoGPTTracker, command_name: str, model: str):
        """
        Initialize command execution context.
        
        Args:
            tracker: AutoGPT tracker instance
            command_name: Name of the command
            model: Model being used
        """
        self.tracker = tracker
        self.command_name = command_name
        self.model = model
        self.execution_id = str(uuid.uuid4())
        self.start_time = None
    
    def __enter__(self):
        """Enter the context manager."""
        self.start_time = time.time()
        
        # Initialize tracking
        self.tracker._execution_start_times[self.execution_id] = self.start_time
        self.tracker._tool_calls[self.execution_id] = []
        self.tracker._memory_events[self.execution_id] = []
        
        # Emit start event
        self.tracker.emitter.emit_agent_event(
            agent_name=f"{self.tracker.agent_name}:{self.command_name}",
            session_id=self.tracker.session_id,
            agent_framework="autogpt",
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
                agent_name=f"{self.tracker.agent_name}:{self.command_name}",
                session_id=self.tracker.session_id,
                agent_framework="autogpt",
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
                agent_name=f"{self.tracker.agent_name}:{self.command_name}",
                session_id=self.tracker.session_id,
                agent_framework="autogpt",
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
        """Log a tool call within this command context."""
        self.tracker.log_tool_call(tool_name, self.execution_id)
    
    def log_memory_event(self, event_type: str, key: str):
        """Log a memory event within this command context."""
        self.tracker.log_memory_event(event_type, key, self.execution_id)