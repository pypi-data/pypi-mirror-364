"""SuperAGI integration for Teraace Agentic Tracker.

SuperAGI is an open-source autonomous AI agent framework that provides
infrastructure for building, managing and running useful autonomous agents.
"""

from typing import Any, Dict, List, Optional, Union
from .base import BaseTracker


class SuperAGITracker(BaseTracker):
    """Tracker for SuperAGI autonomous agents."""
    
    def __init__(self, agent_name: str = "superagi_agent", **kwargs):
        """Initialize SuperAGI tracker."""
        super().__init__(agent_name=agent_name, framework_name="superagi", **kwargs)
        self._tracked_agents = {}
        self._active_runs = {}
    
    def track_agent_creation(self, agent: Any, agent_config: Dict[str, Any]) -> None:
        """Track SuperAGI agent creation.
        
        Args:
            agent: The SuperAGI agent instance
            agent_config: Configuration used to create the agent
        """
        agent_data = {
            'agent_name': agent_config.get('name', 'unknown'),
            'agent_description': agent_config.get('description', ''),
            'model': agent_config.get('model', 'gpt-4'),
            'max_iterations': agent_config.get('max_iterations', 25),
            'tools': agent_config.get('tools', []),
            'tool_count': len(agent_config.get('tools', [])),
            'agent_workflow': agent_config.get('agent_workflow', 'Goal Based Agent'),
            'permission_type': agent_config.get('permission_type', 'God Mode')
        }
        
        self._emit_event(
            event_type='agent_creation',
            data=agent_data,
            metadata={'framework': self.framework_name}
        )
        
        # Store agent for tracking
        agent_id = id(agent)
        self._tracked_agents[agent_id] = agent
    
    def track_agent_run_start(self, agent: Any, goals: List[str], run_id: str = None) -> None:
        """Track the start of a SuperAGI agent run.
        
        Args:
            agent: The agent starting the run
            goals: List of goals for this run
            run_id: Optional run identifier
        """
        run_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'goals': goals,
            'goal_count': len(goals),
            'run_id': run_id,
            'primary_goal': goals[0] if goals else '',
            'start_timestamp': getattr(agent, 'start_time', None)
        }
        
        self._emit_event(
            event_type='agent_run_start',
            data=run_data,
            metadata={'framework': self.framework_name}
        )
        
        # Store run for tracking
        if run_id:
            self._active_runs[run_id] = {'agent': agent, 'goals': goals}
    
    def track_tool_execution(self, agent: Any, tool: Any, tool_input: Dict[str, Any], tool_output: Any) -> None:
        """Track tool execution by SuperAGI agents.
        
        Args:
            agent: The agent using the tool
            tool: The tool being executed
            tool_input: Input provided to the tool
            tool_output: Output from the tool
        """
        tool_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'tool_name': getattr(tool, 'name', tool.__class__.__name__),
            'tool_class': tool.__class__.__name__,
            'input_keys': list(tool_input.keys()) if isinstance(tool_input, dict) else [],
            'has_output': tool_output is not None,
            'output_type': type(tool_output).__name__ if tool_output is not None else None,
            'execution_successful': not isinstance(tool_output, Exception)
        }
        
        self._emit_event(
            event_type='tool_execution',
            data=tool_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_step_execution(self, agent: Any, step: Dict[str, Any], step_result: Dict[str, Any]) -> None:
        """Track individual step execution in SuperAGI.
        
        Args:
            agent: The agent executing the step
            step: The step being executed
            step_result: Result of step execution
        """
        step_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'step_id': step.get('id'),
            'step_type': step.get('type', 'unknown'),
            'step_description': step.get('description', ''),
            'execution_status': step_result.get('status', 'unknown'),
            'tokens_consumed': step_result.get('tokens_consumed', 0),
            'execution_time': step_result.get('execution_time'),
            'has_error': bool(step_result.get('error'))
        }
        
        self._emit_event(
            event_type='step_execution',
            data=step_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_resource_creation(self, agent: Any, resource: Dict[str, Any]) -> None:
        """Track resource creation by SuperAGI agents.
        
        Args:
            agent: The agent creating the resource
            resource: The resource being created
        """
        resource_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'resource_name': resource.get('name', 'unknown'),
            'resource_type': resource.get('type', 'unknown'),
            'resource_size': resource.get('size', 0),
            'resource_path': resource.get('path', ''),
            'creation_timestamp': resource.get('created_at')
        }
        
        self._emit_event(
            event_type='resource_creation',
            data=resource_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_knowledge_update(self, agent: Any, knowledge_type: str, knowledge_data: Dict[str, Any]) -> None:
        """Track knowledge base updates in SuperAGI.
        
        Args:
            agent: The agent updating knowledge
            knowledge_type: Type of knowledge being updated
            knowledge_data: The knowledge data
        """
        knowledge_update_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'knowledge_type': knowledge_type,
            'data_keys': list(knowledge_data.keys()) if isinstance(knowledge_data, dict) else [],
            'data_size': len(str(knowledge_data)),
            'update_timestamp': knowledge_data.get('timestamp')
        }
        
        self._emit_event(
            event_type='knowledge_update',
            data=knowledge_update_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_agent_thinking(self, agent: Any, thoughts: Dict[str, Any]) -> None:
        """Track agent thinking process in SuperAGI.
        
        Args:
            agent: The agent doing the thinking
            thoughts: The agent's thoughts and reasoning
        """
        thinking_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'thoughts': thoughts.get('thoughts', ''),
            'reasoning': thoughts.get('reasoning', ''),
            'plan': thoughts.get('plan', ''),
            'criticism': thoughts.get('criticism', ''),
            'speak': thoughts.get('speak', ''),
            'thoughts_length': len(thoughts.get('thoughts', ''))
        }
        
        self._emit_event(
            event_type='agent_thinking',
            data=thinking_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_iteration_completion(self, agent: Any, iteration_number: int, iteration_summary: Dict[str, Any]) -> None:
        """Track completion of an agent iteration.
        
        Args:
            agent: The agent completing the iteration
            iteration_number: The iteration number
            iteration_summary: Summary of the iteration
        """
        iteration_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'iteration_number': iteration_number,
            'steps_executed': iteration_summary.get('steps_executed', 0),
            'tools_used': iteration_summary.get('tools_used', []),
            'resources_created': iteration_summary.get('resources_created', 0),
            'tokens_consumed': iteration_summary.get('tokens_consumed', 0),
            'iteration_status': iteration_summary.get('status', 'completed')
        }
        
        self._emit_event(
            event_type='iteration_completion',
            data=iteration_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_agent_run_completion(self, agent: Any, run_id: str, run_summary: Dict[str, Any]) -> None:
        """Track completion of a SuperAGI agent run.
        
        Args:
            agent: The agent completing the run
            run_id: The run identifier
            run_summary: Summary of the entire run
        """
        completion_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'run_id': run_id,
            'total_iterations': run_summary.get('total_iterations', 0),
            'total_steps': run_summary.get('total_steps', 0),
            'total_tokens': run_summary.get('total_tokens', 0),
            'goals_achieved': run_summary.get('goals_achieved', []),
            'resources_created': run_summary.get('resources_created', 0),
            'run_status': run_summary.get('status', 'completed'),
            'run_duration': run_summary.get('duration')
        }
        
        self._emit_event(
            event_type='agent_run_completion',
            data=completion_data,
            metadata={'framework': self.framework_name}
        )
        
        # Clean up run tracking
        if run_id in self._active_runs:
            del self._active_runs[run_id]
    
    def auto_track_agent(self, agent: Any, config: Dict[str, Any] = None) -> Any:
        """Automatically track a SuperAGI agent.
        
        Args:
            agent: The SuperAGI agent instance
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
        """Extract model information from SuperAGI agent."""
        if args and hasattr(args[0], 'model'):
            return args[0].model
        return kwargs.get('model', 'gpt-4')
    
    def _emit_event(self, event_type: str, data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Emit a tracking event."""
        # This is a placeholder - in a real implementation, this would emit to the tracking system
        pass