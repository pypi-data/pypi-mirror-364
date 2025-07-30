"""PydanticAI integration for Teraace Agentic Tracker.

PydanticAI supports multiple agent workflows via delegation, hand-offs, and 
graph-based control flow, including agent delegation and stateful graphs.
"""

import time
import uuid
from typing import Any, Dict, List, Optional, Union
from functools import wraps

from .base import BaseTracker


class PydanticAITracker(BaseTracker):
    """Tracker for PydanticAI agents and workflows with multi-agent delegation support."""
    
    def __init__(
        self,
        workflow_name: Optional[str] = None,
        graph_name: Optional[str] = None,
        agent_name: Optional[str] = None,
        session_id: Optional[str] = None,
        config=None,
        run_env: str = "local",
        **metadata
    ):
        """Initialize PydanticAI tracker with flexible workflow/graph/agent support."""
        # Store original parameters
        self.workflow_name = workflow_name
        self.graph_name = graph_name
        self.agent_name_only = agent_name
        self.metadata = metadata
        
        # Determine the primary identifier for tracking
        # Priority: workflow_name > graph_name > agent_name
        if workflow_name and agent_name:
            primary_name = f"{workflow_name}:{agent_name}"
        elif graph_name and agent_name:
            primary_name = f"{graph_name}:{agent_name}"
        elif workflow_name:
            primary_name = workflow_name
        elif graph_name:
            primary_name = graph_name
        elif agent_name:
            primary_name = agent_name
        else:
            primary_name = "pydantic_ai_agent"
        
        # Initialize base tracker
        super().__init__(
            agent_name=primary_name,
            framework_name="pydantic_ai",
            session_id=session_id,
            config=config,
            run_env=run_env
        )
        
        # PydanticAI-specific tracking state
        self._tracked_agents = {}
        self._active_runs = {}
        self._delegation_chains = {}
        self._graph_nodes = {}
    
    def track_agent_creation(self, agent: Any, agent_config: Dict[str, Any] = None, **kwargs) -> None:
        """Track PydanticAI agent creation with workflow context.
        
        Args:
            agent: The PydanticAI agent instance
            agent_config: Configuration for the agent
            **kwargs: Additional agent parameters
        """
        config = agent_config or {}
        agent_data = {
            'agent_name': config.get('name', getattr(agent, 'name', 'unknown')),
            'model': config.get('model', getattr(agent, 'model', 'unknown')),
            'system_prompt': config.get('system_prompt', getattr(agent, 'system_prompt', '')),
            'result_type': config.get('result_type', str(getattr(agent, 'result_type', 'str'))),
            'tools': config.get('tools', getattr(agent, 'tools', [])),
            'tool_count': len(config.get('tools', getattr(agent, 'tools', []))),
            'deps_type': config.get('deps_type', getattr(agent, 'deps_type', None)),
            'retries': config.get('retries', getattr(agent, 'retries', 1)),
            'workflow_name': self.workflow_name,
            'graph_name': self.graph_name,
            'delegation_capable': kwargs.get('delegation_capable', True)
        }
        
        # Log agent creation as a tool call
        self.log_tool_call(f"create_agent_{agent_data['agent_name']}")
        
        # Store agent for tracking
        agent_id = id(agent)
        self._tracked_agents[agent_id] = agent
    
    def track_run_start(self, agent: Any, user_prompt: str, message_history: List[Any] = None, deps: Any = None) -> None:
        """Track start of agent run.
        
        Args:
            agent: The agent starting the run
            user_prompt: User's prompt/message
            message_history: Optional message history
            deps: Optional dependencies
        """
        run_data = {
            'agent_type': agent.__class__.__name__,
            'agent_name': getattr(agent, 'name', 'unknown'),
            'user_prompt': user_prompt,
            'prompt_length': len(user_prompt),
            'has_message_history': message_history is not None,
            'message_history_length': len(message_history) if message_history else 0,
            'has_deps': deps is not None,
            'deps_type': type(deps).__name__ if deps else None,
            'workflow_name': self.workflow_name,
            'graph_name': self.graph_name
        }
        
        # Log run start as a tool call
        self.log_tool_call(f"start_run_{run_data['agent_name']}")
    
    def track_tool_call(self, agent: Any, tool_name: str, tool_args: Dict[str, Any], tool_result: Any) -> None:
        """Track tool execution by the agent.
        
        Args:
            agent: The agent calling the tool
            tool_name: Name of the tool being called
            tool_args: Arguments passed to the tool
            tool_result: Result from the tool execution
        """
        tool_data = {
            'agent_type': agent.__class__.__name__,
            'agent_name': getattr(agent, 'name', 'unknown'),
            'tool_name': tool_name,
            'arg_count': len(tool_args),
            'arg_keys': list(tool_args.keys()) if isinstance(tool_args, dict) else [],
            'has_result': tool_result is not None,
            'result_type': type(tool_result).__name__ if tool_result is not None else None,
            'execution_successful': not isinstance(tool_result, Exception),
            'workflow_name': self.workflow_name,
            'graph_name': self.graph_name
        }
        
        # Log tool execution as a tool call
        self.log_tool_call(f"{tool_data['tool_name']}_{tool_data['agent_name']}")
    
    def track_validation_error(self, agent: Any, error: Any, retry_count: int) -> None:
        """Track validation errors and retries.
        
        Args:
            agent: The agent encountering the error
            error: The validation error
            retry_count: Current retry attempt
        """
        error_data = {
            'agent_type': agent.__class__.__name__,
            'agent_name': getattr(agent, 'name', 'unknown'),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'retry_count': retry_count,
            'is_validation_error': 'validation' in str(error).lower(),
            'workflow_name': self.workflow_name,
            'graph_name': self.graph_name
        }
        
        # Log validation error as a memory event
        self.log_memory_event("validation_error", f"retry_{retry_count}_{error_data['agent_name']}")
    
    def track_result_validation(self, agent: Any, result: Any, validation_success: bool, schema_info: Dict[str, Any] = None) -> None:
        """Track result validation against Pydantic models.
        
        Args:
            agent: The agent producing the result
            result: The result being validated
            validation_success: Whether validation succeeded
            schema_info: Optional schema information
        """
        validation_data = {
            'agent_type': agent.__class__.__name__,
            'agent_name': getattr(agent, 'name', 'unknown'),
            'result_type': type(result).__name__,
            'validation_success': validation_success,
            'schema_name': schema_info.get('schema_name') if schema_info else None,
            'field_count': schema_info.get('field_count') if schema_info else None,
            'required_fields': schema_info.get('required_fields', []) if schema_info else [],
            'result_size': len(str(result)) if result else 0,
            'workflow_name': self.workflow_name,
            'graph_name': self.graph_name
        }
        
        # Log result validation as a memory event
        self.log_memory_event("result_validation", f"{'success' if validation_success else 'failure'}_{validation_data['agent_name']}")
    
    def track_streaming_response(self, agent: Any, chunk_count: int, total_tokens: int = None) -> None:
        """Track streaming response from agent.
        
        Args:
            agent: The agent providing streaming response
            chunk_count: Number of chunks received
            total_tokens: Optional total token count
        """
        streaming_data = {
            'agent_type': agent.__class__.__name__,
            'agent_name': getattr(agent, 'name', 'unknown'),
            'chunk_count': chunk_count,
            'total_tokens': total_tokens,
            'has_token_info': total_tokens is not None,
            'avg_chunk_size': total_tokens / chunk_count if total_tokens and chunk_count > 0 else None,
            'workflow_name': self.workflow_name,
            'graph_name': self.graph_name
        }
        
        # Log streaming response as a tool call
        self.log_tool_call(f"stream_response_{streaming_data['agent_name']}")
    
    def track_dependency_injection(self, agent: Any, deps: Any, injection_successful: bool) -> None:
        """Track dependency injection into agent.
        
        Args:
            agent: The agent receiving dependencies
            deps: The dependencies being injected
            injection_successful: Whether injection was successful
        """
        deps_data = {
            'agent_type': agent.__class__.__name__,
            'agent_name': getattr(agent, 'name', 'unknown'),
            'deps_type': type(deps).__name__,
            'injection_successful': injection_successful,
            'deps_attributes': list(vars(deps).keys()) if hasattr(deps, '__dict__') else [],
            'attribute_count': len(vars(deps)) if hasattr(deps, '__dict__') else 0,
            'workflow_name': self.workflow_name,
            'graph_name': self.graph_name
        }
        
        # Log dependency injection as a memory event
        self.log_memory_event("dependency_injection", f"{'success' if injection_successful else 'failure'}_{deps_data['agent_name']}")
    
    def track_run_completion(self, agent: Any, final_result: Any, run_stats: Dict[str, Any]) -> None:
        """Track completion of agent run.
        
        Args:
            agent: The agent completing the run
            final_result: Final result from the run
            run_stats: Statistics about the run
        """
        completion_data = {
            'agent_type': agent.__class__.__name__,
            'agent_name': getattr(agent, 'name', 'unknown'),
            'result_type': type(final_result).__name__,
            'run_successful': run_stats.get('successful', True),
            'total_tokens': run_stats.get('total_tokens', 0),
            'tool_calls_made': run_stats.get('tool_calls', 0),
            'retry_count': run_stats.get('retries', 0),
            'execution_time': run_stats.get('execution_time'),
            'cost_estimate': run_stats.get('cost_estimate'),
            'workflow_name': self.workflow_name,
            'graph_name': self.graph_name
        }
        
        # Log run completion as a tool call
        self.log_tool_call(f"complete_run_{completion_data['agent_name']}")
    
    def track_model_response(self, agent: Any, model_response: Dict[str, Any]) -> None:
        """Track raw model response details.
        
        Args:
            agent: The agent receiving the response
            model_response: Raw response from the model
        """
        response_data = {
            'agent_type': agent.__class__.__name__,
            'agent_name': getattr(agent, 'name', 'unknown'),
            'model_name': model_response.get('model', 'unknown'),
            'prompt_tokens': model_response.get('usage', {}).get('prompt_tokens', 0),
            'completion_tokens': model_response.get('usage', {}).get('completion_tokens', 0),
            'total_tokens': model_response.get('usage', {}).get('total_tokens', 0),
            'finish_reason': model_response.get('choices', [{}])[0].get('finish_reason'),
            'response_time': model_response.get('response_time'),
            'workflow_name': self.workflow_name,
            'graph_name': self.graph_name
        }
        
        # Log model response as a tool call
        self.log_tool_call(f"model_response_{response_data['agent_name']}")
    
    def track_agent_delegation(self, from_agent: Any, to_agent: Any, delegation_context: Dict[str, Any]) -> None:
        """Track agent delegation in multi-agent workflows.
        
        Args:
            from_agent: Agent delegating the task
            to_agent: Agent receiving the delegation
            delegation_context: Context and data for the delegation
        """
        delegation_data = {
            'from_agent': getattr(from_agent, 'name', 'unknown'),
            'to_agent': getattr(to_agent, 'name', 'unknown'),
            'context_keys': list(delegation_context.keys()) if isinstance(delegation_context, dict) else [],
            'context_size': len(str(delegation_context)),
            'workflow_name': self.workflow_name,
            'graph_name': self.graph_name,
            'delegation_id': str(uuid.uuid4())
        }
        
        # Log delegation as a memory event
        self.log_memory_event("agent_delegation", f"{delegation_data['from_agent']}_to_{delegation_data['to_agent']}")
        
        # Track delegation chain
        delegation_id = delegation_data['delegation_id']
        self._delegation_chains[delegation_id] = {
            'from_agent': from_agent,
            'to_agent': to_agent,
            'context': delegation_context,
            'timestamp': time.time()
        }
    
    def track_graph_node_execution(self, node_name: str, agent: Any, input_data: Any, output_data: Any = None) -> None:
        """Track execution of graph nodes in PydanticAI workflows.
        
        Args:
            node_name: Name of the graph node
            agent: Agent executing the node
            input_data: Input data to the node
            output_data: Output data from the node
        """
        node_data = {
            'node_name': node_name,
            'agent_name': getattr(agent, 'name', 'unknown'),
            'agent_type': agent.__class__.__name__,
            'input_type': type(input_data).__name__,
            'has_output': output_data is not None,
            'output_type': type(output_data).__name__ if output_data else None,
            'workflow_name': self.workflow_name,
            'graph_name': self.graph_name
        }
        
        # Log graph node execution as a tool call
        self.log_tool_call(f"execute_node_{node_data['node_name']}_{node_data['agent_name']}")
        
        # Store node execution
        self._graph_nodes[node_name] = {
            'agent': agent,
            'input_data': input_data,
            'output_data': output_data,
            'timestamp': time.time()
        }
    
    def track_workflow_state_update(self, state_key: str, state_value: Any, agent: Any = None) -> None:
        """Track workflow state updates across multiple agents.
        
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
            'workflow_name': self.workflow_name,
            'graph_name': self.graph_name,
            'timestamp': time.time()
        }
        
        # Log state update as a memory event
        self.log_memory_event("workflow_state", f"update_{state_key}")
    
    def auto_track_agent(self, agent: Any, config: Dict[str, Any] = None) -> Any:
        """Automatically track a PydanticAI agent.
        
        Args:
            agent: The PydanticAI agent instance
            config: Optional agent configuration
            
        Returns:
            The same agent (for chaining)
        """
        agent_id = id(agent)
        self._tracked_agents[agent_id] = agent
        
        # Track agent creation if config is provided
        if config:
            self.track_agent_creation(agent, config)
        
        return agent
    
    def extract_model_info(self, *args, **kwargs) -> str:
        """Extract model information from PydanticAI agent."""
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
    
    def track_workflow_context(self, workflow_name: str, model: str = "unknown"):
        """Context manager for tracking workflow execution."""
        return WorkflowExecutionContext(self, workflow_name, model)
    
    @classmethod
    def auto_track_workflow(cls, workflow_name: str, agent_names: List[str], **tracker_kwargs):
        """
        Automatically set up tracking for a PydanticAI workflow with multiple agents.
        This is the easiest way to get started - just specify the workflow and agent names.
        """
        trackers = {}
        for agent_name in agent_names:
            tracker = cls(workflow_name=workflow_name, agent_name=agent_name, **tracker_kwargs)
            trackers[agent_name] = tracker
        
        return trackers if len(agent_names) > 1 else trackers[agent_names[0]]
    
    @classmethod
    def auto_track_graph(cls, graph_name: str, agent_names: List[str], **tracker_kwargs):
        """
        Automatically set up tracking for a PydanticAI graph with multiple agents.
        """
        trackers = {}
        for agent_name in agent_names:
            tracker = cls(graph_name=graph_name, agent_name=agent_name, **tracker_kwargs)
            trackers[agent_name] = tracker
        
        return trackers if len(agent_names) > 1 else trackers[agent_names[0]]


class WorkflowExecutionContext:
    """Context manager for tracking PydanticAI workflow execution."""
    
    def __init__(self, tracker: PydanticAITracker, workflow_name: str, model: str):
        self.tracker = tracker
        self.workflow_name = workflow_name
        self.model = model
        self.execution_id = str(uuid.uuid4())
        self.start_time = None
    
    def __enter__(self):
        """Enter the context manager - start tracking."""
        self.start_time = time.time()
        self.tracker.start_operation(self.execution_id)
        self.tracker.emit_lifecycle_event("start", 0, self.model, True, agent_name_suffix=self.workflow_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager - end tracking."""
        try:
            duration_ms = self.tracker.end_operation(self.execution_id)
            tool_calls, memory_events = self.tracker.get_operation_data(self.execution_id)
            
            if exc_type is None:
                self.tracker.emit_lifecycle_event("end", duration_ms, self.model, True,
                                                agent_name_suffix=self.workflow_name,
                                                tool_calls=tool_calls, memory_events=memory_events)
            else:
                self.tracker.emit_lifecycle_event("error", duration_ms, self.model, False,
                                                agent_name_suffix=self.workflow_name,
                                                exception=exc_type.__name__ if exc_type else "",
                                                tool_calls=tool_calls, memory_events=memory_events)
        finally:
            self.tracker.cleanup_operation(self.execution_id)
    
    def log_tool_call(self, tool_name: str):
        """Log a tool call within this workflow context."""
        self.tracker.log_tool_call(tool_name, self.execution_id)
    
    def log_memory_event(self, event_type: str, key: str):
        """Log a memory event within this workflow context."""
        self.tracker.log_memory_event(event_type, key, self.execution_id)