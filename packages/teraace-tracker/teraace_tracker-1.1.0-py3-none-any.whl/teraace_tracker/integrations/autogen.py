"""AutoGen integration for Teraace Agentic Tracker.

AutoGen is Microsoft's multi-agent conversation framework that enables
multiple AI agents to collaborate and have conversations to solve tasks.
"""

import time
import uuid
from typing import Any, Dict, List, Optional, Union
from functools import wraps

from .base import BaseTracker


class AutoGenTracker(BaseTracker):
    """Tracker for AutoGen multi-agent conversations with team support."""
    
    def __init__(
        self,
        team_name: Optional[str] = None,
        agent_name: Optional[str] = None,
        session_id: Optional[str] = None,
        config=None,
        run_env: str = "local",
        **metadata
    ):
        """Initialize AutoGen tracker with flexible team/agent support."""
        # Store original parameters
        self.team_name = team_name
        self.agent_name_only = agent_name
        self.metadata = metadata
        
        # Determine the primary identifier for tracking
        if team_name and agent_name:
            primary_name = f"{team_name}:{agent_name}"
        elif team_name:
            primary_name = team_name
        elif agent_name:
            primary_name = agent_name
        else:
            primary_name = "autogen_team"
        
        # Initialize base tracker
        super().__init__(
            agent_name=primary_name,
            framework_name="autogen",
            session_id=session_id,
            config=config,
            run_env=run_env
        )
        
        # AutoGen-specific tracking state
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
        
        # Log agent creation as a tool call for tracking
        self.log_tool_call(f"create_agent_{agent_data['agent_name']}")
        
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
        
        # Log conversation start as a memory event
        self.log_memory_event("conversation_start", f"{conversation_data['initiator_name']}_to_{conversation_data['recipient_name']}")
    
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
        
        # Log message exchange as a memory event
        self.log_memory_event("message_exchange", f"{message_data['sender_name']}_to_{message_data['recipient_name']}")
        
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
        
        # Log function call as a tool call
        self.log_tool_call(f"{function_data['agent_name']}_{function_name}")
    
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
        
        # Log group chat as a memory event
        self.log_memory_event("group_chat", f"group_{len(group_data['agent_names'])}_agents")
    
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
        
        # Log conversation end as a memory event
        self.log_memory_event("conversation_end", f"total_messages_{total_messages}")
        
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
    
    def track_conversation_execution(self, conversation_name: str, model: str = "unknown"):
        """Context manager for tracking conversation execution."""
        return ConversationExecutionContext(self, conversation_name, model)
    
    @classmethod
    def auto_track_team(cls, team_name: str, *agents, **tracker_kwargs):
        """
        Automatically set up tracking for a team of AutoGen agents.
        This is the easiest way to get started - just wrap your agents.
        """
        tracker = cls(team_name=team_name, **tracker_kwargs)
        
        # Track all agents in the team
        for agent in agents:
            agent_id = id(agent)
            tracker._tracked_agents[agent_id] = agent
            
            # Track agent creation if config is available
            if hasattr(agent, '_llm_config'):
                tracker.track_agent_creation(agent, {'llm_config': agent._llm_config})
        
        return tracker

class ConversationExecutionContext:
    """Context manager for tracking AutoGen conversation execution."""
    
    def __init__(self, tracker: AutoGenTracker, conversation_name: str, model: str):
        self.tracker = tracker
        self.conversation_name = conversation_name
        self.model = model
        self.execution_id = str(uuid.uuid4())
        self.start_time = None
    
    def __enter__(self):
        """Enter the context manager - start tracking."""
        self.start_time = time.time()
        self.tracker.start_operation(self.execution_id)
        self.tracker.emit_lifecycle_event("start", 0, self.model, True, agent_name_suffix=self.conversation_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager - end tracking."""
        try:
            duration_ms = self.tracker.end_operation(self.execution_id)
            tool_calls, memory_events = self.tracker.get_operation_data(self.execution_id)
            
            if exc_type is None:
                self.tracker.emit_lifecycle_event("end", duration_ms, self.model, True,
                                                agent_name_suffix=self.conversation_name,
                                                tool_calls=tool_calls, memory_events=memory_events)
            else:
                self.tracker.emit_lifecycle_event("error", duration_ms, self.model, False,
                                                agent_name_suffix=self.conversation_name,
                                                exception=exc_type.__name__ if exc_type else "",
                                                tool_calls=tool_calls, memory_events=memory_events)
        finally:
            self.tracker.cleanup_operation(self.execution_id)
    
    def log_tool_call(self, tool_name: str):
        """Log a tool call within this conversation context."""
        self.tracker.log_tool_call(tool_name, self.execution_id)
    
    def log_memory_event(self, event_type: str, key: str):
        """Log a memory event within this conversation context."""
        self.tracker.log_memory_event(event_type, key, self.execution_id)