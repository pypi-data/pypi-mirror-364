"""CAMEL integration for Teraace Agentic Tracker.

CAMEL (Communicative Agents for "Mind" Exploration of Large Scale Language Model Society)
is a framework for studying cooperative behavior and capabilities of multi-agent systems.
"""

import time
import uuid
from typing import Any, Dict, List, Optional, Union
from functools import wraps

from .base import BaseTracker


class CAMELTracker(BaseTracker):
    """Tracker for CAMEL multi-agent communication with society/workforce support."""
    
    def __init__(
        self,
        society_name: Optional[str] = None,
        workforce_name: Optional[str] = None,
        agent_role: Optional[str] = None,
        session_id: Optional[str] = None,
        config=None,
        run_env: str = "local",
        **metadata
    ):
        """Initialize CAMEL tracker with flexible society/workforce/role support."""
        # Store original parameters
        self.society_name = society_name
        self.workforce_name = workforce_name
        self.agent_role_only = agent_role
        self.metadata = metadata
        
        # Determine the primary identifier for tracking
        # Priority: society_name > workforce_name > agent_role
        if society_name and agent_role:
            primary_name = f"{society_name}:{agent_role}"
        elif workforce_name and agent_role:
            primary_name = f"{workforce_name}:{agent_role}"
        elif society_name:
            primary_name = society_name
        elif workforce_name:
            primary_name = workforce_name
        elif agent_role:
            primary_name = agent_role
        else:
            primary_name = "camel_society"
        
        # Initialize base tracker
        super().__init__(
            agent_name=primary_name,
            framework_name="camel",
            session_id=session_id,
            config=config,
            run_env=run_env
        )
        
        # CAMEL-specific tracking state
        self._tracked_societies = {}
        self._conversation_history = []
    
    def track_society_creation(self, society: Any, society_config: Dict[str, Any]) -> None:
        """Track creation of a CAMEL society.
        
        Args:
            society: The CAMEL society instance
            society_config: Configuration for the society
        """
        society_data = {
            'society_name': society_config.get('name', 'unknown'),
            'agent_count': society_config.get('agent_count', 2),
            'task_type': society_config.get('task_type', 'unknown'),
            'model_type': society_config.get('model_type', 'gpt-3.5-turbo'),
            'max_turns': society_config.get('max_turns', 10),
            'temperature': society_config.get('temperature', 0.7)
        }
        
        # Log society creation as a memory event
        self.log_memory_event("society_creation", f"{society_data['society_name']}_{society_data['agent_count']}_agents")
        
        # Store society for tracking
        society_id = id(society)
        self._tracked_societies[society_id] = society
    
    def track_agent_creation(self, agent: Any, role_config: Dict[str, Any]) -> None:
        """Track creation of a CAMEL agent with specific role.
        
        Args:
            agent: The CAMEL agent instance
            role_config: Configuration for the agent's role
        """
        agent_data = {
            'agent_type': agent.__class__.__name__,
            'role_name': role_config.get('role_name', 'unknown'),
            'role_description': role_config.get('role_description', ''),
            'system_message': role_config.get('system_message', ''),
            'model_config': role_config.get('model_config', {}),
            'has_memory': role_config.get('has_memory', False)
        }
        
        # Log agent creation as a tool call
        self.log_tool_call(f"create_agent_{agent_data['role_name']}")
    
    def track_task_specification(self, task: Dict[str, Any], agents: List[Any]) -> None:
        """Track task specification in CAMEL.
        
        Args:
            task: The task specification
            agents: List of agents involved in the task
        """
        task_data = {
            'task_id': task.get('id'),
            'task_description': task.get('description', ''),
            'task_type': task.get('type', 'unknown'),
            'agent_count': len(agents),
            'agent_roles': [getattr(agent, 'role_name', 'unknown') for agent in agents],
            'task_complexity': task.get('complexity', 'medium'),
            'expected_turns': task.get('expected_turns', 10)
        }
        
        # Log task specification as a tool call
        self.log_tool_call(f"specify_task_{task_data['task_type']}")
    
    def track_role_playing_start(self, assistant_agent: Any, user_agent: Any, task: str) -> None:
        """Track the start of role-playing between agents.
        
        Args:
            assistant_agent: The assistant agent
            user_agent: The user agent
            task: The task they are working on
        """
        roleplay_data = {
            'assistant_role': getattr(assistant_agent, 'role_name', 'assistant'),
            'user_role': getattr(user_agent, 'role_name', 'user'),
            'task': task,
            'task_length': len(task),
            'start_timestamp': getattr(assistant_agent, 'start_time', None)
        }
        
        # Log role playing start as a memory event
        self.log_memory_event("role_playing_start", f"{roleplay_data['assistant_role']}_vs_{roleplay_data['user_role']}")
    
    def track_message_exchange(self, sender: Any, receiver: Any, message: Dict[str, Any], turn_number: int) -> None:
        """Track message exchange between CAMEL agents.
        
        Args:
            sender: The agent sending the message
            receiver: The agent receiving the message
            message: The message content and metadata
            turn_number: The current turn number
        """
        exchange_data = {
            'sender_role': getattr(sender, 'role_name', 'unknown'),
            'receiver_role': getattr(receiver, 'role_name', 'unknown'),
            'message_content': message.get('content', ''),
            'message_type': message.get('type', 'text'),
            'turn_number': turn_number,
            'message_length': len(message.get('content', '')),
            'has_function_call': 'function_call' in message,
            'timestamp': message.get('timestamp')
        }
        
        # Log message exchange as a memory event
        self.log_memory_event("message_exchange", f"{exchange_data['sender_role']}_to_{exchange_data['receiver_role']}_turn_{turn_number}")
        
        # Store in conversation history
        self._conversation_history.append(exchange_data)
    
    def track_solution_extraction(self, solution: str, conversation_history: List[Dict[str, Any]]) -> None:
        """Track solution extraction from conversation.
        
        Args:
            solution: The extracted solution
            conversation_history: History of the conversation
        """
        solution_data = {
            'solution': solution,
            'solution_length': len(solution),
            'conversation_turns': len(conversation_history),
            'solution_quality': self._assess_solution_quality(solution),
            'extraction_successful': len(solution.strip()) > 0
        }
        
        # Log solution extraction as a tool call
        self.log_tool_call(f"extract_solution_{solution_data['solution_quality']}")
    
    def track_cooperation_analysis(self, agents: List[Any], cooperation_metrics: Dict[str, Any]) -> None:
        """Track cooperation analysis between agents.
        
        Args:
            agents: List of agents being analyzed
            cooperation_metrics: Metrics about their cooperation
        """
        cooperation_data = {
            'agent_count': len(agents),
            'agent_roles': [getattr(agent, 'role_name', 'unknown') for agent in agents],
            'cooperation_score': cooperation_metrics.get('cooperation_score', 0.0),
            'communication_efficiency': cooperation_metrics.get('communication_efficiency', 0.0),
            'task_completion_rate': cooperation_metrics.get('task_completion_rate', 0.0),
            'conflict_resolution_count': cooperation_metrics.get('conflict_resolution_count', 0)
        }
        
        # Log cooperation analysis as a tool call
        self.log_tool_call(f"analyze_cooperation_{cooperation_data['agent_count']}_agents")
    
    def track_role_playing_completion(self, assistant_agent: Any, user_agent: Any, final_result: Dict[str, Any]) -> None:
        """Track completion of role-playing session.
        
        Args:
            assistant_agent: The assistant agent
            user_agent: The user agent
            final_result: Final result of the role-playing session
        """
        completion_data = {
            'assistant_role': getattr(assistant_agent, 'role_name', 'assistant'),
            'user_role': getattr(user_agent, 'role_name', 'user'),
            'total_turns': final_result.get('total_turns', 0),
            'task_completed': final_result.get('task_completed', False),
            'solution_found': final_result.get('solution_found', False),
            'cooperation_rating': final_result.get('cooperation_rating', 0.0),
            'session_duration': final_result.get('duration'),
            'termination_reason': final_result.get('termination_reason', 'unknown')
        }
        
        # Log role playing completion as a memory event
        self.log_memory_event("role_playing_completion", f"{completion_data['assistant_role']}_vs_{completion_data['user_role']}_turns_{completion_data['total_turns']}")
        
        # Clear conversation history
        self._conversation_history.clear()
    
    def track_emergent_behavior(self, behavior_type: str, behavior_data: Dict[str, Any], agents_involved: List[Any]) -> None:
        """Track emergent behaviors in CAMEL societies.
        
        Args:
            behavior_type: Type of emergent behavior observed
            behavior_data: Data about the behavior
            agents_involved: Agents that exhibited the behavior
        """
        emergent_data = {
            'behavior_type': behavior_type,
            'agent_count': len(agents_involved),
            'agent_roles': [getattr(agent, 'role_name', 'unknown') for agent in agents_involved],
            'behavior_strength': behavior_data.get('strength', 0.0),
            'behavior_duration': behavior_data.get('duration'),
            'behavior_context': behavior_data.get('context', ''),
            'is_beneficial': behavior_data.get('is_beneficial', True)
        }
        
        # Log emergent behavior as a tool call
        self.log_tool_call(f"emergent_{behavior_type}_{emergent_data['agent_count']}_agents")
    
    def _assess_solution_quality(self, solution: str) -> str:
        """Assess the quality of a solution (simple heuristic).
        
        Args:
            solution: The solution text
            
        Returns:
            Quality assessment (high, medium, low)
        """
        if len(solution) > 200 and any(word in solution.lower() for word in ['because', 'therefore', 'however', 'moreover']):
            return 'high'
        elif len(solution) > 50:
            return 'medium'
        else:
            return 'low'
    
    def auto_track_society(self, society: Any, config: Dict[str, Any] = None) -> Any:
        """Automatically track a CAMEL society.
        
        Args:
            society: The CAMEL society instance
            config: Optional society configuration
            
        Returns:
            The same society (for chaining)
        """
        society_id = id(society)
        self._tracked_societies[society_id] = society
        
        # Track society creation if config is provided
        if config:
            self.track_society_creation(society, config)
        
        return society
    
    def extract_model_info(self, *args, **kwargs) -> str:
        """Extract model information from CAMEL society."""
        return kwargs.get('model_type', 'gpt-3.5-turbo')
    
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
    
    def track_society_execution(self, society_name: str, model: str = "unknown"):
        """Context manager for tracking society execution."""
        return SocietyExecutionContext(self, society_name, model)
    
    @classmethod
    def auto_track_society_with_roles(cls, society_name: str, agent_roles: List[str], **tracker_kwargs):
        """
        Automatically set up tracking for a CAMEL society with multiple roles.
        This is the easiest way to get started - just specify the society and roles.
        """
        trackers = {}
        for role in agent_roles:
            tracker = cls(society_name=society_name, agent_role=role, **tracker_kwargs)
            trackers[role] = tracker
        
        return trackers if len(agent_roles) > 1 else trackers[agent_roles[0]]
    
    @classmethod
    def auto_track_workforce(cls, workforce_name: str, agent_roles: List[str], **tracker_kwargs):
        """
        Automatically set up tracking for a CAMEL workforce with multiple roles.
        """
        trackers = {}
        for role in agent_roles:
            tracker = cls(workforce_name=workforce_name, agent_role=role, **tracker_kwargs)
            trackers[role] = tracker
        
        return trackers if len(agent_roles) > 1 else trackers[agent_roles[0]]

class SocietyExecutionContext:
    """Context manager for tracking CAMEL society execution."""
    
    def __init__(self, tracker: CAMELTracker, society_name: str, model: str):
        self.tracker = tracker
        self.society_name = society_name
        self.model = model
        self.execution_id = str(uuid.uuid4())
        self.start_time = None
    
    def __enter__(self):
        """Enter the context manager - start tracking."""
        self.start_time = time.time()
        self.tracker.start_operation(self.execution_id)
        self.tracker.emit_lifecycle_event("start", 0, self.model, True, agent_name_suffix=self.society_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager - end tracking."""
        try:
            duration_ms = self.tracker.end_operation(self.execution_id)
            tool_calls, memory_events = self.tracker.get_operation_data(self.execution_id)
            
            if exc_type is None:
                self.tracker.emit_lifecycle_event("end", duration_ms, self.model, True,
                                                agent_name_suffix=self.society_name,
                                                tool_calls=tool_calls, memory_events=memory_events)
            else:
                self.tracker.emit_lifecycle_event("error", duration_ms, self.model, False,
                                                agent_name_suffix=self.society_name,
                                                exception=exc_type.__name__ if exc_type else "",
                                                tool_calls=tool_calls, memory_events=memory_events)
        finally:
            self.tracker.cleanup_operation(self.execution_id)
    
    def log_tool_call(self, tool_name: str):
        """Log a tool call within this society context."""
        self.tracker.log_tool_call(tool_name, self.execution_id)
    
    def log_memory_event(self, event_type: str, key: str):
        """Log a memory event within this society context."""
        self.tracker.log_memory_event(event_type, key, self.execution_id)