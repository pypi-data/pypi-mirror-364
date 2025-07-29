"""AutoGen integration for Teraace Agentic Tracker.

AutoGen is Microsoft's multi-agent conversation framework that enables
multiple AI agents to collaborate and have conversations to solve tasks.
"""

from typing import Any, Dict, List, Optional, Union
from .base import BaseTracker


class AutoGenTracker(BaseTracker):
    """Tracker for AutoGen multi-agent conversations."""
    
    def __init__(self, agent_name: str = "autogen_agent", **kwargs):
        """Initialize AutoGen tracker."""
        super().__init__(agent_name=agent_name, framework_name="autogen", **kwargs)
        self._tracked_agents = {}
        self._conversation_history = []
    
    def track_agent_creation(self, agent: Any, agent_config: Dict[str, Any]) -> None:
        """Track agent creation and configuration.
        
        Args:
            agent: The AutoGen agent instance
            agent_config: Configuration used to create the agent
        """
        agent_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'agent_type': agent.__class__.__name__,
            'system_message': getattr(agent, 'system_message', ''),
            'llm_config': agent_config.get('llm_config', {}),
            'human_input_mode': getattr(agent, 'human_input_mode', 'NEVER'),
            'max_consecutive_auto_reply': getattr(agent, 'max_consecutive_auto_reply', None)
        }
        
        self._emit_event(
            event_type='agent_creation',
            data=agent_data,
            metadata={'framework': self.framework_name}
        )
        
        # Store agent for conversation tracking
        agent_id = id(agent)
        self._tracked_agents[agent_id] = agent
    
    def track_conversation_start(self, initiator: Any, recipient: Any, message: str, **kwargs) -> None:
        """Track the start of a conversation between agents.
        
        Args:
            initiator: The agent starting the conversation
            recipient: The agent receiving the message
            message: The initial message
            **kwargs: Additional conversation parameters
        """
        conversation_data = {
            'initiator_name': getattr(initiator, 'name', 'unknown'),
            'initiator_type': initiator.__class__.__name__,
            'recipient_name': getattr(recipient, 'name', 'unknown'),
            'recipient_type': recipient.__class__.__name__,
            'initial_message': message,
            'max_turns': kwargs.get('max_turns'),
            'silent': kwargs.get('silent', False)
        }
        
        self._emit_event(
            event_type='conversation_start',
            data=conversation_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_message_exchange(self, sender: Any, recipient: Any, message: Dict[str, Any]) -> None:
        """Track individual message exchanges between agents.
        
        Args:
            sender: The agent sending the message
            recipient: The agent receiving the message
            message: The message content and metadata
        """
        message_data = {
            'sender_name': getattr(sender, 'name', 'unknown'),
            'sender_type': sender.__class__.__name__,
            'recipient_name': getattr(recipient, 'name', 'unknown'),
            'recipient_type': recipient.__class__.__name__,
            'content': message.get('content', ''),
            'role': message.get('role', 'user'),
            'function_call': message.get('function_call'),
            'name': message.get('name')
        }
        
        self._emit_event(
            event_type='message_exchange',
            data=message_data,
            metadata={'framework': self.framework_name}
        )
        
        # Store in conversation history
        self._conversation_history.append(message_data)
    
    def track_function_call(self, agent: Any, function_name: str, arguments: Dict[str, Any], result: Any = None) -> None:
        """Track function calls made by agents.
        
        Args:
            agent: The agent making the function call
            function_name: Name of the function being called
            arguments: Arguments passed to the function
            result: Result of the function call (if available)
        """
        function_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'agent_type': agent.__class__.__name__,
            'function_name': function_name,
            'arguments': arguments,
            'has_result': result is not None,
            'result_type': type(result).__name__ if result is not None else None
        }
        
        self._emit_event(
            event_type='function_call',
            data=function_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_group_chat(self, group_chat: Any, messages: List[Dict[str, Any]]) -> None:
        """Track group chat sessions with multiple agents.
        
        Args:
            group_chat: The GroupChat instance
            messages: List of messages in the group chat
        """
        group_data = {
            'agent_count': len(getattr(group_chat, 'agents', [])),
            'agent_names': [getattr(agent, 'name', 'unknown') for agent in getattr(group_chat, 'agents', [])],
            'message_count': len(messages),
            'max_round': getattr(group_chat, 'max_round', None),
            'admin_name': getattr(getattr(group_chat, 'admin_name', None), 'name', None) if hasattr(group_chat, 'admin_name') else None
        }
        
        self._emit_event(
            event_type='group_chat',
            data=group_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_conversation_end(self, summary: Optional[str] = None, total_messages: int = 0) -> None:
        """Track the end of a conversation.
        
        Args:
            summary: Optional summary of the conversation
            total_messages: Total number of messages exchanged
        """
        end_data = {
            'summary': summary,
            'total_messages': total_messages,
            'conversation_length': len(self._conversation_history)
        }
        
        self._emit_event(
            event_type='conversation_end',
            data=end_data,
            metadata={'framework': self.framework_name}
        )
        
        # Clear conversation history
        self._conversation_history.clear()
    
    def auto_track_agents(self, *agents) -> tuple:
        """Automatically track multiple AutoGen agents.
        
        Args:
            *agents: Variable number of AutoGen agent instances
            
        Returns:
            tuple: The same agents passed in (for chaining)
        """
        for agent in agents:
            agent_id = id(agent)
            self._tracked_agents[agent_id] = agent
            
            # Track agent creation if config is available
            if hasattr(agent, '_llm_config'):
                self.track_agent_creation(agent, {'llm_config': agent._llm_config})
        
        return agents if len(agents) > 1 else agents[0] if agents else None
    
    def extract_model_info(self, *args, **kwargs) -> str:
        """Extract model information from AutoGen agent."""
        if args and hasattr(args[0], '_llm_config'):
            config = args[0]._llm_config
            if isinstance(config, dict) and 'config_list' in config:
                config_list = config['config_list']
                if config_list and isinstance(config_list[0], dict):
                    return config_list[0].get('model', 'gpt-4')
        return kwargs.get('model', 'gpt-4')
    
    def _emit_event(self, event_type: str, data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Emit a tracking event."""
        # This is a placeholder - in a real implementation, this would emit to the tracking system
        pass