"""Swarm integration for Teraace Agentic Tracker.

Swarm is OpenAI's experimental multi-agent orchestration framework
that focuses on lightweight, controllable, and testable agent coordination.
"""

from typing import Any, Dict, List, Optional, Union, Callable
from .base import BaseTracker


class SwarmTracker(BaseTracker):
    """Tracker for OpenAI Swarm multi-agent orchestration."""
    
    def __init__(self, agent_name: str = "swarm_agent", **kwargs):
        """Initialize Swarm tracker."""
        super().__init__(agent_name=agent_name, framework_name="swarm", **kwargs)
        self._tracked_agents = {}
        self._active_conversations = {}
    
    def track_agent_creation(self, agent: Any, agent_config: Dict[str, Any]) -> None:
        """Track Swarm agent creation and configuration.
        
        Args:
            agent: The Swarm agent instance
            agent_config: Configuration used to create the agent
        """
        agent_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'agent_type': agent.__class__.__name__,
            'model': getattr(agent, 'model', 'gpt-4'),
            'instructions': getattr(agent, 'instructions', ''),
            'function_count': len(getattr(agent, 'functions', [])),
            'tool_choice': getattr(agent, 'tool_choice', None),
            'parallel_tool_calls': getattr(agent, 'parallel_tool_calls', True)
        }
        
        self._emit_event(
            event_type='agent_creation',
            data=agent_data,
            metadata={'framework': self.framework_name}
        )
        
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
            'debug': kwargs.get('debug', False)
        }
        
        self._emit_event(
            event_type='swarm_run_start',
            data=run_data,
            metadata={'framework': self.framework_name}
        )
    
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
            'context_size': len(str(context))
        }
        
        self._emit_event(
            event_type='agent_handoff',
            data=handoff_data,
            metadata={'framework': self.framework_name}
        )
    
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
            'result_type': type(result).__name__ if result is not None else None
        }
        
        self._emit_event(
            event_type='function_execution',
            data=function_data,
            metadata={'framework': self.framework_name}
        )
    
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
            'modified_keys': [k for k in old_context.keys() if k in new_context and old_context[k] != new_context[k]] if isinstance(new_context, dict) and isinstance(old_context, dict) else []
        }
        
        self._emit_event(
            event_type='context_update',
            data=context_data,
            metadata={'framework': self.framework_name}
        )
    
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
            'usage': response.get('usage', {})
        }
        
        self._emit_event(
            event_type='response_generation',
            data=response_data,
            metadata={'framework': self.framework_name}
        )
    
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
            'conversation_turns': len([m for m in messages if m.get('role') == 'user'])
        }
        
        self._emit_event(
            event_type='swarm_completion',
            data=completion_data,
            metadata={'framework': self.framework_name}
        )
    
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
    
    def _emit_event(self, event_type: str, data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Emit a tracking event."""
        # This is a placeholder - in a real implementation, this would emit to the tracking system
        pass