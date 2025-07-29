"""PydanticAI integration for Teraace Agentic Tracker.

PydanticAI is a Python agent framework designed to make it less painful to build
production-grade applications with generative AI.
"""

from typing import Any, Dict, List, Optional, Union
from .base import BaseTracker


class PydanticAITracker(BaseTracker):
    """Tracker for PydanticAI agents and workflows."""
    
    def __init__(self, agent_name: str = "pydantic_ai_agent", **kwargs):
        """Initialize PydanticAI tracker."""
        super().__init__(agent_name=agent_name, framework_name="pydantic_ai", **kwargs)
        self._tracked_agents = {}
        self._active_runs = {}
    
    def track_agent_creation(self, agent: Any, agent_config: Dict[str, Any]) -> None:
        """Track PydanticAI agent creation.
        
        Args:
            agent: The PydanticAI agent instance
            agent_config: Configuration for the agent
        """
        agent_data = {
            'agent_name': agent_config.get('name', 'unknown'),
            'model': agent_config.get('model', 'unknown'),
            'system_prompt': agent_config.get('system_prompt', ''),
            'result_type': agent_config.get('result_type', 'str'),
            'tools': agent_config.get('tools', []),
            'tool_count': len(agent_config.get('tools', [])),
            'deps_type': agent_config.get('deps_type', None),
            'retries': agent_config.get('retries', 1)
        }
        
        self._emit_event(
            event_type='agent_creation',
            data=agent_data,
            metadata={'framework': self.framework_name}
        )
        
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
            'user_prompt': user_prompt,
            'prompt_length': len(user_prompt),
            'has_message_history': message_history is not None,
            'message_history_length': len(message_history) if message_history else 0,
            'has_deps': deps is not None,
            'deps_type': type(deps).__name__ if deps else None
        }
        
        self._emit_event(
            event_type='run_start',
            data=run_data,
            metadata={'framework': self.framework_name}
        )
    
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
            'tool_name': tool_name,
            'arg_count': len(tool_args),
            'arg_keys': list(tool_args.keys()) if isinstance(tool_args, dict) else [],
            'has_result': tool_result is not None,
            'result_type': type(tool_result).__name__ if tool_result is not None else None,
            'execution_successful': not isinstance(tool_result, Exception)
        }
        
        self._emit_event(
            event_type='tool_call',
            data=tool_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_validation_error(self, agent: Any, error: Any, retry_count: int) -> None:
        """Track validation errors and retries.
        
        Args:
            agent: The agent encountering the error
            error: The validation error
            retry_count: Current retry attempt
        """
        error_data = {
            'agent_type': agent.__class__.__name__,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'retry_count': retry_count,
            'is_validation_error': 'validation' in str(error).lower()
        }
        
        self._emit_event(
            event_type='validation_error',
            data=error_data,
            metadata={'framework': self.framework_name}
        )
    
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
            'result_type': type(result).__name__,
            'validation_success': validation_success,
            'schema_name': schema_info.get('schema_name') if schema_info else None,
            'field_count': schema_info.get('field_count') if schema_info else None,
            'required_fields': schema_info.get('required_fields', []) if schema_info else [],
            'result_size': len(str(result)) if result else 0
        }
        
        self._emit_event(
            event_type='result_validation',
            data=validation_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_streaming_response(self, agent: Any, chunk_count: int, total_tokens: int = None) -> None:
        """Track streaming response from agent.
        
        Args:
            agent: The agent providing streaming response
            chunk_count: Number of chunks received
            total_tokens: Optional total token count
        """
        streaming_data = {
            'agent_type': agent.__class__.__name__,
            'chunk_count': chunk_count,
            'total_tokens': total_tokens,
            'has_token_info': total_tokens is not None,
            'avg_chunk_size': total_tokens / chunk_count if total_tokens and chunk_count > 0 else None
        }
        
        self._emit_event(
            event_type='streaming_response',
            data=streaming_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_dependency_injection(self, agent: Any, deps: Any, injection_successful: bool) -> None:
        """Track dependency injection into agent.
        
        Args:
            agent: The agent receiving dependencies
            deps: The dependencies being injected
            injection_successful: Whether injection was successful
        """
        deps_data = {
            'agent_type': agent.__class__.__name__,
            'deps_type': type(deps).__name__,
            'injection_successful': injection_successful,
            'deps_attributes': list(vars(deps).keys()) if hasattr(deps, '__dict__') else [],
            'attribute_count': len(vars(deps)) if hasattr(deps, '__dict__') else 0
        }
        
        self._emit_event(
            event_type='dependency_injection',
            data=deps_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_run_completion(self, agent: Any, final_result: Any, run_stats: Dict[str, Any]) -> None:
        """Track completion of agent run.
        
        Args:
            agent: The agent completing the run
            final_result: Final result from the run
            run_stats: Statistics about the run
        """
        completion_data = {
            'agent_type': agent.__class__.__name__,
            'result_type': type(final_result).__name__,
            'run_successful': run_stats.get('successful', True),
            'total_tokens': run_stats.get('total_tokens', 0),
            'tool_calls_made': run_stats.get('tool_calls', 0),
            'retry_count': run_stats.get('retries', 0),
            'execution_time': run_stats.get('execution_time'),
            'cost_estimate': run_stats.get('cost_estimate')
        }
        
        self._emit_event(
            event_type='run_completion',
            data=completion_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_model_response(self, agent: Any, model_response: Dict[str, Any]) -> None:
        """Track raw model response details.
        
        Args:
            agent: The agent receiving the response
            model_response: Raw response from the model
        """
        response_data = {
            'agent_type': agent.__class__.__name__,
            'model_name': model_response.get('model', 'unknown'),
            'prompt_tokens': model_response.get('usage', {}).get('prompt_tokens', 0),
            'completion_tokens': model_response.get('usage', {}).get('completion_tokens', 0),
            'total_tokens': model_response.get('usage', {}).get('total_tokens', 0),
            'finish_reason': model_response.get('choices', [{}])[0].get('finish_reason'),
            'response_time': model_response.get('response_time')
        }
        
        self._emit_event(
            event_type='model_response',
            data=response_data,
            metadata={'framework': self.framework_name}
        )
    
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
    
    def _emit_event(self, event_type: str, data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Emit a tracking event."""
        # This is a placeholder - in a real implementation, this would emit to the tracking system
        pass