"""CAMEL integration for Teraace Agentic Tracker.

CAMEL (Communicative Agents for "Mind" Exploration of Large Scale Language Model Society)
is a framework for studying cooperative behavior and capabilities of multi-agent systems.
"""

from typing import Any, Dict, List, Optional, Union
from .base import BaseTracker


class CAMELTracker(BaseTracker):
    """Tracker for CAMEL multi-agent communication."""
    
    def __init__(self, agent_name: str = "camel_agent", **kwargs):
        """Initialize CAMEL tracker."""
        super().__init__(agent_name=agent_name, framework_name="camel", **kwargs)
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
        
        self._emit_event(
            event_type='society_creation',
            data=society_data,
            metadata={'framework': self.framework_name}
        )
        
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
        
        self._emit_event(
            event_type='agent_creation',
            data=agent_data,
            metadata={'framework': self.framework_name}
        )
    
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
        
        self._emit_event(
            event_type='task_specification',
            data=task_data,
            metadata={'framework': self.framework_name}
        )
    
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
        
        self._emit_event(
            event_type='role_playing_start',
            data=roleplay_data,
            metadata={'framework': self.framework_name}
        )
    
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
        
        self._emit_event(
            event_type='message_exchange',
            data=exchange_data,
            metadata={'framework': self.framework_name}
        )
        
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
        
        self._emit_event(
            event_type='solution_extraction',
            data=solution_data,
            metadata={'framework': self.framework_name}
        )
    
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
        
        self._emit_event(
            event_type='cooperation_analysis',
            data=cooperation_data,
            metadata={'framework': self.framework_name}
        )
    
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
        
        self._emit_event(
            event_type='role_playing_completion',
            data=completion_data,
            metadata={'framework': self.framework_name}
        )
        
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
        
        self._emit_event(
            event_type='emergent_behavior',
            data=emergent_data,
            metadata={'framework': self.framework_name}
        )
    
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
    
    def _emit_event(self, event_type: str, data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Emit a tracking event."""
        # This is a placeholder - in a real implementation, this would emit to the tracking system
        pass