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
    """Semantic Kernel integration for tracking agent events with multi-agent group chat support."""
    
    def __init__(
        self,
        agent_name: str = None,
        group_name: Optional[str] = None,
        chat_name: Optional[str] = None,
        workflow_name: Optional[str] = None,
        session_id: Optional[str] = None,
        config: Optional[Config] = None,
        run_env: str = "local"
    ):
        """
        Initialize Semantic Kernel tracker with multi-agent group chat support.
        
        Args:
            agent_name: Name of the agent being tracked
            group_name: Name of the agent group/chat
            chat_name: Name of the specific chat session
            workflow_name: Name of the workflow
            session_id: Session identifier (auto-generated if not provided)
            config: Teraace configuration
            run_env: Runtime environment ('local', 'cloud', etc.)
        """
        # Store original parameters
        self.group_name = group_name
        self.chat_name = chat_name
        self.workflow_name = workflow_name
        self.agent_name_only = agent_name
        
        # Determine the primary identifier for tracking
        # Priority: group_name > chat_name > workflow_name > agent_name
        if group_name and agent_name:
            primary_name = f"{group_name}:{agent_name}"
        elif chat_name and agent_name:
            primary_name = f"{chat_name}:{agent_name}"
        elif workflow_name and agent_name:
            primary_name = f"{workflow_name}:{agent_name}"
        elif group_name:
            primary_name = group_name
        elif chat_name:
            primary_name = chat_name
        elif workflow_name:
            primary_name = workflow_name
        elif agent_name:
            primary_name = agent_name
        else:
            primary_name = "semantic_kernel_agent"
        
        super().__init__(primary_name, "semantic_kernel", session_id, config, run_env)
        
        # Semantic Kernel-specific tracking state
        self._tracked_agents = {}
        self._group_chats = {}
        self._chat_history = {}
        
        logger.info(f"Semantic Kernel tracker initialized for agent '{primary_name}' session '{self.session_id}'")
    
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
    
    def track_agent_group_chat(self, group_chat: Any, agents: List[Any], **kwargs) -> None:
        """Track AgentGroupChat creation and configuration.
        
        Args:
            group_chat: The AgentGroupChat instance
            agents: List of agents in the group chat
            **kwargs: Additional group chat parameters
        """
        chat_data = {
            'group_chat_type': group_chat.__class__.__name__,
            'agent_count': len(agents),
            'agent_names': [getattr(agent, 'name', agent.__class__.__name__) for agent in agents],
            'agent_types': [agent.__class__.__name__ for agent in agents],
            'termination_strategy': kwargs.get('termination_strategy', 'unknown'),
            'max_turns': kwargs.get('max_turns'),
            'group_name': self.group_name,
            'chat_name': self.chat_name,
            'workflow_name': self.workflow_name
        }
        
        # Log group chat creation as a tool call
        self.log_tool_call(f"create_group_chat_{len(agents)}_agents")
        
        # Store group chat for tracking
        chat_id = id(group_chat)
        self._group_chats[chat_id] = {
            'group_chat': group_chat,
            'agents': agents,
            'chat_data': chat_data
        }
    
    def track_agent_message(self, agent: Any, message: str, message_type: str = "user") -> None:
        """Track messages sent by agents in group chats.
        
        Args:
            agent: The agent sending the message
            message: The message content
            message_type: Type of message (user, assistant, system)
        """
        message_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'agent_type': agent.__class__.__name__,
            'message_type': message_type,
            'message_length': len(message),
            'group_name': self.group_name,
            'chat_name': self.chat_name,
            'workflow_name': self.workflow_name,
            'timestamp': time.time()
        }
        
        # Log agent message as a memory event
        self.log_memory_event("agent_message", f"{message_data['agent_name']}_{message_type}")
        
        # Store in chat history
        if not hasattr(self, '_chat_history'):
            self._chat_history = []
        self._chat_history.append(message_data)
    
    def track_agent_selection(self, selector_agent: Any, selected_agent: Any, selection_reason: str = None) -> None:
        """Track agent selection in group chats.
        
        Args:
            selector_agent: Agent making the selection
            selected_agent: Agent being selected
            selection_reason: Reason for the selection
        """
        selection_data = {
            'selector_name': getattr(selector_agent, 'name', 'unknown'),
            'selected_name': getattr(selected_agent, 'name', 'unknown'),
            'selection_reason': selection_reason,
            'group_name': self.group_name,
            'chat_name': self.chat_name,
            'workflow_name': self.workflow_name
        }
        
        # Log agent selection as a memory event
        self.log_memory_event("agent_selection", f"{selection_data['selector_name']}_selects_{selection_data['selected_name']}")
    
    def track_termination_strategy(self, strategy: Any, termination_reason: str, final_agent: Any = None) -> None:
        """Track termination strategy execution in group chats.
        
        Args:
            strategy: The termination strategy instance
            termination_reason: Reason for termination
            final_agent: Optional final agent that triggered termination
        """
        termination_data = {
            'strategy_type': strategy.__class__.__name__,
            'termination_reason': termination_reason,
            'final_agent': getattr(final_agent, 'name', 'unknown') if final_agent else None,
            'group_name': self.group_name,
            'chat_name': self.chat_name,
            'workflow_name': self.workflow_name
        }
        
        # Log termination as a tool call
        self.log_tool_call(f"terminate_chat_{termination_data['strategy_type']}")
    
    def track_group_chat_execution(self, group_chat: Any, input_message: str, final_response: str = None) -> None:
        """Track complete group chat execution.
        
        Args:
            group_chat: The group chat instance
            input_message: Initial input message
            final_response: Final response from the chat
        """
        execution_data = {
            'group_chat_type': group_chat.__class__.__name__,
            'input_length': len(input_message),
            'has_response': final_response is not None,
            'response_length': len(final_response) if final_response else 0,
            'group_name': self.group_name,
            'chat_name': self.chat_name,
            'workflow_name': self.workflow_name
        }
        
        # Log group chat execution as a tool call
        self.log_tool_call(f"execute_group_chat_{execution_data['group_chat_type']}")
    
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
    
    @classmethod
    def auto_track_group_chat(cls, group_name: str, agent_names: List[str], **tracker_kwargs):
        """
        Automatically set up tracking for a Semantic Kernel group chat with multiple agents.
        This is the easiest way to get started - just specify the group and agent names.
        """
        trackers = {}
        for agent_name in agent_names:
            tracker = cls(agent_name=agent_name, group_name=group_name, **tracker_kwargs)
            trackers[agent_name] = tracker
        
        return trackers if len(agent_names) > 1 else trackers[agent_names[0]]
    
    @classmethod
    def auto_track_workflow(cls, workflow_name: str, agent_names: List[str], **tracker_kwargs):
        """
        Automatically set up tracking for a Semantic Kernel workflow with multiple agents.
        """
        trackers = {}
        for agent_name in agent_names:
            tracker = cls(agent_name=agent_name, workflow_name=workflow_name, **tracker_kwargs)
            trackers[agent_name] = tracker
        
        return trackers if len(agent_names) > 1 else trackers[agent_names[0]]


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


