"""Swarm integration for Teraace Agentic Tracker.

OpenAI's Swarm provides two primitives: Agent and handoff, enabling agents 
to pass control to one another, collaborate, and execute workflows in a 
stateless client loop.
"""

import time
import uuid
from typing import Any, Dict, List, Optional, Union, Callable
from functools import wraps

from .base import BaseTracker


class SwarmTracker(BaseTracker):
    """Tracker for OpenAI Swarm multi-agent orchestration with routine/workflow support."""
    
    def __init__(
        self,
        routine_name: Optional[str] = None,
        workflow_name: Optional[str] = None,
        agent_name: Optional[str] = None,
        session_id: Optional[str] = None,
        config=None,
        run_env: str = "local",
        **metadata
    ):
        """Initialize Swarm tracker with flexible routine/workflow/agent support."""
        # Store original parameters
        self.routine_name = routine_name
        self.workflow_name = workflow_name
        self.agent_name_only = agent_name
        self.metadata = metadata
        
        # Determine the primary identifier for tracking
        # Priority: routine_name > workflow_name > agent_name
        if routine_name and agent_name:
            primary_name = f"{routine_name}:{agent_name}"
        elif workflow_name and agent_name:
            primary_name = f"{workflow_name}:{agent_name}"
        elif routine_name:
            primary_name = routine_name
        elif workflow_name:
            primary_name = workflow_name
        elif agent_name:
            primary_name = agent_name
        else:
            primary_name = "swarm_agent"
        
        # Initialize base tracker
        super().__init__(
            agent_name=primary_name,
            framework_name="swarm",
            session_id=session_id,
            config=config,
            run_env=run_env
        )
        
        # Swarm-specific tracking state
        self._tracked_agents = {}
        self._active_conversations = {}
        self._handoff_chains = {}
        self._routine_state = {}
    
    def track_agent_creation(self, agent: Any, agent_config: Dict[str, Any] = None, **kwargs) -> None:
        """Track Swarm agent creation and configuration.
        
        Args:
            agent: The Swarm agent instance
            agent_config: Configuration used to create the agent
            **kwargs: Additional agent parameters
        """
        config = agent_config or {}
        agent_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'agent_type': agent.__class__.__name__,
            'model': getattr(agent, 'model', 'gpt-4'),
            'instructions': getattr(agent, 'instructions', ''),
            'function_count': len(getattr(agent, 'functions', [])),
            'function_names': [getattr(f, '__name__', 'unknown') for f in getattr(agent, 'functions', [])],
            'tool_choice': getattr(agent, 'tool_choice', None),
            'parallel_tool_calls': getattr(agent, 'parallel_tool_calls', True),
            'routine_name': self.routine_name,
            'workflow_name': self.workflow_name,
            'handoff_capable': kwargs.get('handoff_capable', True)
        }
        
        # Log agent creation as a tool call
        self.log_tool_call(f"create_agent_{agent_data['agent_name']}")
        
        # Store agent for tracking
        agent_id = id(agent)
        self._tracked_agents[agent_id] = agent
    
    def track_swarm_run(self, client: Any, agent: Any, messages: List[Dict[str, Any]], **kwargs) -> None:
        """Track a Swarm run execution.
        
        Args:
            client: The Swarm client
            agent: The starting agent
            messages: List of messages in the conversation
            **kwargs: Additional run parameters
        """
        run_data = {
            'starting_agent': getattr(agent, 'name', 'unknown'),
            'agent_type': agent.__class__.__name__,
            'message_count': len(messages),
            'context_variables': kwargs.get('context_variables', {}),
            'max_turns': kwargs.get('max_turns'),
            'model_override': kwargs.get('model_override'),
            'execute_tools': kwargs.get('execute_tools', True),
            'stream': kwargs.get('stream', False),
            'debug': kwargs.get('debug', False),
            'routine_name': self.routine_name,
            'workflow_name': self.workflow_name
        }
        
        # Log swarm run start as a tool call
        self.log_tool_call(f"start_swarm_run_{run_data['starting_agent']}")
    
    def track_agent_handoff(self, from_agent: Any, to_agent: Any, context: Dict[str, Any]) -> None:
        """Track agent handoffs during execution.
        
        Args:
            from_agent: The agent handing off control
            to_agent: The agent receiving control
            context: Context variables passed during handoff
        """
        handoff_data = {
            'from_agent': getattr(from_agent, 'name', 'unknown'),
            'from_agent_type': from_agent.__class__.__name__,
            'to_agent': getattr(to_agent, 'name', 'unknown'),
            'to_agent_type': to_agent.__class__.__name__,
            'context_keys': list(context.keys()) if isinstance(context, dict) else [],
            'context_size': len(str(context)),
            'routine_name': self.routine_name,
            'workflow_name': self.workflow_name
        }
        
        # Log handoff as a memory event
        self.log_memory_event("agent_handoff", f"{handoff_data['from_agent']}_to_{handoff_data['to_agent']}")
        
        # Track handoff chain
        handoff_id = str(uuid.uuid4())
        self._handoff_chains[handoff_id] = {
            'from_agent': from_agent,
            'to_agent': to_agent,
            'context': context,
            'timestamp': time.time()
        }
    
    def track_function_execution(self, agent: Any, function: Callable, arguments: Dict[str, Any], result: Any = None) -> None:
        """Track function executions by agents.
        
        Args:
            agent: The agent executing the function
            function: The function being executed
            arguments: Arguments passed to the function
            result: Result of the function execution
        """
        function_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'function_name': getattr(function, '__name__', 'unknown'),
            'function_module': getattr(function, '__module__', 'unknown'),
            'arguments': arguments,
            'has_result': result is not None,
            'result_type': type(result).__name__ if result is not None else None,
            'routine_name': self.routine_name,
            'workflow_name': self.workflow_name
        }
        
        # Log function execution as a tool call
        self.log_tool_call(f"{function_data['function_name']}_{function_data['agent_name']}")
    
    def track_context_update(self, agent: Any, old_context: Dict[str, Any], new_context: Dict[str, Any]) -> None:
        """Track context variable updates.
        
        Args:
            agent: The agent updating context
            old_context: Previous context variables
            new_context: Updated context variables
        """
        context_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'old_keys': list(old_context.keys()) if isinstance(old_context, dict) else [],
            'new_keys': list(new_context.keys()) if isinstance(new_context, dict) else [],
            'added_keys': list(set(new_context.keys()) - set(old_context.keys())) if isinstance(new_context, dict) and isinstance(old_context, dict) else [],
            'removed_keys': list(set(old_context.keys()) - set(new_context.keys())) if isinstance(new_context, dict) and isinstance(old_context, dict) else [],
            'modified_keys': [k for k in old_context.keys() if k in new_context and old_context[k] != new_context[k]] if isinstance(new_context, dict) and isinstance(old_context, dict) else [],
            'routine_name': self.routine_name,
            'workflow_name': self.workflow_name
        }
        
        # Log context update as a memory event
        self.log_memory_event("context_update", f"{context_data['agent_name']}_context")
    
    def track_response_generation(self, agent: Any, messages: List[Dict[str, Any]], response: Dict[str, Any]) -> None:
        """Track response generation by agents.
        
        Args:
            agent: The agent generating the response
            messages: Input messages
            response: Generated response
        """
        response_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'input_message_count': len(messages),
            'response_content': response.get('content', ''),
            'response_role': response.get('role', 'assistant'),
            'tool_calls': len(response.get('tool_calls', [])),
            'finish_reason': response.get('finish_reason'),
            'usage': response.get('usage', {}),
            'routine_name': self.routine_name,
            'workflow_name': self.workflow_name
        }
        
        # Log response generation as a tool call
        self.log_tool_call(f"generate_response_{response_data['agent_name']}")
    
    def track_swarm_completion(self, final_agent: Any, messages: List[Dict[str, Any]], context: Dict[str, Any]) -> None:
        """Track completion of a Swarm run.
        
        Args:
            final_agent: The final agent that completed the run
            messages: Final message history
            context: Final context variables
        """
        completion_data = {
            'final_agent': getattr(final_agent, 'name', 'unknown'),
            'final_agent_type': final_agent.__class__.__name__,
            'total_messages': len(messages),
            'final_context_keys': list(context.keys()) if isinstance(context, dict) else [],
            'conversation_turns': len([m for m in messages if m.get('role') == 'user']),
            'routine_name': self.routine_name,
            'workflow_name': self.workflow_name
        }
        
        # Log swarm completion as a tool call
        self.log_tool_call(f"complete_swarm_{completion_data['final_agent']}")
    
    def track_routine_state_update(self, state_key: str, state_value: Any, agent: Any = None) -> None:
        """Track routine state updates across multiple agents.
        
        Args:
            state_key: The state key being updated
            state_value: The new state value
            agent: Optional agent making the update
        """
        state_data = {
            'state_key': state_key,
            'state_type': type(state_value).__name__,
            'state_size': len(str(state_value)),
            'updating_agent': getattr(agent, 'name', 'system') if agent else 'system',
            'routine_name': self.routine_name,
            'workflow_name': self.workflow_name,
            'timestamp': time.time()
        }
        
        # Update routine state
        self._routine_state[state_key] = state_value
        
        # Log state update as a memory event
        self.log_memory_event("routine_state", f"update_{state_key}")
    
    def track_multi_agent_coordination(self, coordinator: Any, agents: List[Any], coordination_type: str = "handoff_chain") -> None:
        """Track coordination between multiple agents in a routine.
        
        Args:
            coordinator: The coordinating agent or system
            agents: List of agents being coordinated
            coordination_type: Type of coordination (handoff_chain, parallel, broadcast)
        """
        coordination_data = {
            'coordinator_name': getattr(coordinator, 'name', 'system') if coordinator else 'system',
            'agent_count': len(agents),
            'agent_names': [getattr(agent, 'name', f'agent_{i}') for i, agent in enumerate(agents)],
            'coordination_type': coordination_type,
            'routine_name': self.routine_name,
            'workflow_name': self.workflow_name
        }
        
        # Log coordination as a memory event
        self.log_memory_event("multi_agent_coordination", f"{coordination_type}_{len(agents)}_agents")
    
    def auto_track_agents(self, *agents) -> tuple:
        """Automatically track multiple Swarm agents.
        
        Args:
            *agents: Variable number of Swarm agent instances
            
        Returns:
            tuple: The same agents passed in (for chaining)
        """
        for agent in agents:
            agent_id = id(agent)
            self._tracked_agents[agent_id] = agent
            
            # Track agent creation
            config = {
                'model': getattr(agent, 'model', 'gpt-4'),
                'instructions': getattr(agent, 'instructions', ''),
                'functions': getattr(agent, 'functions', [])
            }
            self.track_agent_creation(agent, config)
        
        return agents if len(agents) > 1 else agents[0] if agents else None
    
    def extract_model_info(self, *args, **kwargs) -> str:
        """Extract model information from Swarm agent."""
        if args and hasattr(args[0], 'model'):
            return args[0].model
        return kwargs.get('model', 'gpt-4')
    
    def track_agent_execution(self, func):
        """Decorator for tracking agent execution."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            execution_id = str(uuid.uuid4())
            
            self.start_operation(execution_id)
            model = self.extract_model_info(*args, **kwargs)
            self.emit_lifecycle_event("start", 0, model, True)
            
            try:
                result = func(*args, **kwargs)
                duration_ms = self.end_operation(execution_id)
                tool_calls, memory_events = self.get_operation_data(execution_id)
                
                self.emit_lifecycle_event("end", duration_ms, model, True,
                                        tool_calls=tool_calls, memory_events=memory_events)
                return result
                
            except Exception as e:
                duration_ms = self.end_operation(execution_id)
                tool_calls, memory_events = self.get_operation_data(execution_id)
                
                self.emit_lifecycle_event("error", duration_ms, model, False,
                                        exception=type(e).__name__,
                                        tool_calls=tool_calls, memory_events=memory_events)
                raise
            finally:
                self.cleanup_operation(execution_id)
        
        return wrapper
    
    def track_routine_context(self, routine_name: str, model: str = "unknown"):
        """Context manager for tracking routine execution."""
        return RoutineExecutionContext(self, routine_name, model)
    
    @classmethod
    def auto_track_routine(cls, routine_name: str, agent_names: List[str], **tracker_kwargs):
        """
        Automatically set up tracking for a Swarm routine with multiple agents.
        This is the easiest way to get started - just specify the routine and agent names.
        """
        trackers = {}
        for agent_name in agent_names:
            tracker = cls(routine_name=routine_name, agent_name=agent_name, **tracker_kwargs)
            trackers[agent_name] = tracker
        
        return trackers if len(agent_names) > 1 else trackers[agent_names[0]]
    
    @classmethod
    def auto_track_workflow(cls, workflow_name: str, agent_names: List[str], **tracker_kwargs):
        """
        Automatically set up tracking for a Swarm workflow with multiple agents.
        """
        trackers = {}
        for agent_name in agent_names:
            tracker = cls(workflow_name=workflow_name, agent_name=agent_name, **tracker_kwargs)
            trackers[agent_name] = tracker
        
        return trackers if len(agent_names) > 1 else trackers[agent_names[0]]


class RoutineExecutionContext:
    """Context manager for tracking Swarm routine execution."""
    
    def __init__(self, tracker: SwarmTracker, routine_name: str, model: str):
        self.tracker = tracker
        self.routine_name = routine_name
        self.model = model
        self.execution_id = str(uuid.uuid4())
        self.start_time = None
    
    def __enter__(self):
        """Enter the context manager - start tracking."""
        self.start_time = time.time()
        self.tracker.start_operation(self.execution_id)
        self.tracker.emit_lifecycle_event("start", 0, self.model, True, agent_name_suffix=self.routine_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager - end tracking."""
        try:
            duration_ms = self.tracker.end_operation(self.execution_id)
            tool_calls, memory_events = self.tracker.get_operation_data(self.execution_id)
            
            if exc_type is None:
                self.tracker.emit_lifecycle_event("end", duration_ms, self.model, True,
                                                agent_name_suffix=self.routine_name,
                                                tool_calls=tool_calls, memory_events=memory_events)
            else:
                self.tracker.emit_lifecycle_event("error", duration_ms, self.model, False,
                                                agent_name_suffix=self.routine_name,
                                                exception=exc_type.__name__ if exc_type else "",
                                                tool_calls=tool_calls, memory_events=memory_events)
        finally:
            self.tracker.cleanup_operation(self.execution_id)
    
    def log_tool_call(self, tool_name: str):
        """Log a tool call within this routine context."""
        self.tracker.log_tool_call(tool_name, self.execution_id)
    
    def log_memory_event(self, event_type: str, key: str):
        """Log a memory event within this routine context."""
        self.tracker.log_memory_event(event_type, key, self.execution_id)