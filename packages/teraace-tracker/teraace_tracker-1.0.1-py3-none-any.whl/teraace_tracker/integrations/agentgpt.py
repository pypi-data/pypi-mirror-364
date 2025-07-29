"""AgentGPT integration for Teraace Agentic Tracker.

AgentGPT is a web-based autonomous AI agent platform that allows users
to create and deploy AI agents for various tasks.
"""

from typing import Any, Dict, List, Optional, Union
from .base import BaseTracker


class AgentGPTTracker(BaseTracker):
    """Tracker for AgentGPT autonomous agents."""
    
    def __init__(self, agent_name: str = "agentgpt_agent", **kwargs):
        """Initialize AgentGPT tracker."""
        super().__init__(agent_name=agent_name, framework_name="agentgpt", **kwargs)
        self._tracked_agents = {}
        self._active_runs = {}
    
    def track_agent_creation(self, agent: Any, agent_config: Dict[str, Any]) -> None:
        """Track AgentGPT agent creation.
        
        Args:
            agent: The AgentGPT agent instance
            agent_config: Configuration used to create the agent
        """
        agent_data = {
            'agent_name': agent_config.get('name', 'unknown'),
            'agent_goal': agent_config.get('goal', ''),
            'model_name': agent_config.get('model', 'gpt-3.5-turbo'),
            'max_iterations': agent_config.get('max_iterations', 5),
            'temperature': agent_config.get('temperature', 0.7),
            'language': agent_config.get('language', 'en'),
            'agent_type': agent.__class__.__name__
        }
        
        self._emit_event(
            event_type='agent_creation',
            data=agent_data,
            metadata={'framework': self.framework_name}
        )
        
        # Store agent for tracking
        agent_id = id(agent)
        self._tracked_agents[agent_id] = agent
    
    def track_agent_run_start(self, agent: Any, goal: str, run_id: str = None) -> None:
        """Track the start of an AgentGPT run.
        
        Args:
            agent: The agent starting the run
            goal: The goal for this run
            run_id: Optional run identifier
        """
        run_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'goal': goal,
            'run_id': run_id,
            'goal_length': len(goal),
            'start_timestamp': getattr(agent, 'start_time', None)
        }
        
        self._emit_event(
            event_type='agent_run_start',
            data=run_data,
            metadata={'framework': self.framework_name}
        )
        
        # Store run for tracking
        if run_id:
            self._active_runs[run_id] = {'agent': agent, 'goal': goal}
    
    def track_task_creation(self, agent: Any, task: Dict[str, Any], task_id: str = None) -> None:
        """Track task creation within an agent run.
        
        Args:
            agent: The agent creating the task
            task: The task details
            task_id: Optional task identifier
        """
        task_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'task_id': task_id,
            'task_type': task.get('type', 'unknown'),
            'task_description': task.get('description', ''),
            'task_priority': task.get('priority', 'normal'),
            'estimated_difficulty': task.get('difficulty', 'medium')
        }
        
        self._emit_event(
            event_type='task_creation',
            data=task_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_task_execution(self, agent: Any, task: Dict[str, Any], execution_result: Dict[str, Any]) -> None:
        """Track task execution by the agent.
        
        Args:
            agent: The agent executing the task
            task: The task being executed
            execution_result: Result of task execution
        """
        execution_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'task_id': task.get('id'),
            'task_type': task.get('type', 'unknown'),
            'execution_status': execution_result.get('status', 'unknown'),
            'execution_time': execution_result.get('execution_time'),
            'tokens_used': execution_result.get('tokens_used'),
            'has_output': bool(execution_result.get('output')),
            'has_error': bool(execution_result.get('error'))
        }
        
        self._emit_event(
            event_type='task_execution',
            data=execution_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_thinking_process(self, agent: Any, thought: str, reasoning: str = None) -> None:
        """Track the agent's thinking process.
        
        Args:
            agent: The agent doing the thinking
            thought: The agent's current thought
            reasoning: Optional reasoning behind the thought
        """
        thinking_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'thought': thought,
            'reasoning': reasoning,
            'thought_length': len(thought),
            'has_reasoning': reasoning is not None
        }
        
        self._emit_event(
            event_type='thinking_process',
            data=thinking_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_web_search(self, agent: Any, query: str, search_results: List[Dict[str, Any]]) -> None:
        """Track web search operations by the agent.
        
        Args:
            agent: The agent performing the search
            query: The search query
            search_results: Results from the web search
        """
        search_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'query': query,
            'result_count': len(search_results),
            'query_length': len(query),
            'top_result_title': search_results[0].get('title', '') if search_results else ''
        }
        
        self._emit_event(
            event_type='web_search',
            data=search_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_file_operation(self, agent: Any, operation: str, file_path: str, operation_result: Dict[str, Any]) -> None:
        """Track file operations performed by the agent.
        
        Args:
            agent: The agent performing the file operation
            operation: Type of file operation (read, write, create, delete)
            file_path: Path to the file
            operation_result: Result of the file operation
        """
        file_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'operation': operation,
            'file_path': file_path,
            'file_extension': file_path.split('.')[-1] if '.' in file_path else '',
            'operation_status': operation_result.get('status', 'unknown'),
            'file_size': operation_result.get('file_size'),
            'has_error': bool(operation_result.get('error'))
        }
        
        self._emit_event(
            event_type='file_operation',
            data=file_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_iteration_completion(self, agent: Any, iteration_number: int, iteration_result: Dict[str, Any]) -> None:
        """Track completion of an agent iteration.
        
        Args:
            agent: The agent completing the iteration
            iteration_number: The iteration number
            iteration_result: Result of the iteration
        """
        iteration_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'iteration_number': iteration_number,
            'tasks_completed': iteration_result.get('tasks_completed', 0),
            'tasks_created': iteration_result.get('tasks_created', 0),
            'iteration_status': iteration_result.get('status', 'unknown'),
            'tokens_used': iteration_result.get('tokens_used', 0),
            'iteration_duration': iteration_result.get('duration')
        }
        
        self._emit_event(
            event_type='iteration_completion',
            data=iteration_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_agent_run_completion(self, agent: Any, run_id: str, final_result: Dict[str, Any]) -> None:
        """Track completion of an AgentGPT run.
        
        Args:
            agent: The agent completing the run
            run_id: The run identifier
            final_result: Final result of the run
        """
        completion_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'run_id': run_id,
            'total_iterations': final_result.get('total_iterations', 0),
            'total_tasks': final_result.get('total_tasks', 0),
            'completion_status': final_result.get('status', 'unknown'),
            'total_tokens': final_result.get('total_tokens', 0),
            'run_duration': final_result.get('duration'),
            'goal_achieved': final_result.get('goal_achieved', False)
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
        """Automatically track an AgentGPT agent.
        
        Args:
            agent: The AgentGPT agent instance
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
        """Extract model information from AgentGPT agent."""
        if args and hasattr(args[0], 'model'):
            return args[0].model
        return kwargs.get('model', 'gpt-3.5-turbo')
    
    def _emit_event(self, event_type: str, data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Emit a tracking event."""
        # This is a placeholder - in a real implementation, this would emit to the tracking system
        pass