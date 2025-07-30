"""AgentGPT integration for Teraace Agentic Tracker.

AgentGPT is a web-based autonomous AI agent platform that allows users
to create and deploy AI agents for various tasks. Based on general AutoGPT 
clones, AgentGPT is likely single autonomous agent with multi-tool capabilities, 
not full multi-agent orchestration.

Note: AgentGPT does not have evidence of sub-agent workflows or collaboration,
so multi-agent naming considerations are not applicable.
"""

import time
import uuid
from typing import Any, Dict, List, Optional, Union
from functools import wraps

from .base import BaseTracker


class AgentGPTTracker(BaseTracker):
    """Tracker for AgentGPT autonomous agents (single-agent focused)."""
    
    def __init__(
        self,
        agent_name: str = "agentgpt_agent",
        session_id: Optional[str] = None,
        config=None,
        run_env: str = "local",
        **kwargs
    ):
        """Initialize AgentGPT tracker for single-agent operations."""
        super().__init__(
            agent_name=agent_name, 
            framework_name="agentgpt",
            session_id=session_id,
            config=config,
            run_env=run_env
        )
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
        
        # Log agent creation as a tool call
        self.log_tool_call(f"create_agent_{agent_data['agent_name']}")
        
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
            'run_id': run_id or str(uuid.uuid4()),
            'goal_length': len(goal),
            'start_timestamp': getattr(agent, 'start_time', time.time())
        }
        
        # Log run start as a tool call
        self.log_tool_call(f"start_run_{run_data['agent_name']}")
        
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
        
        # Log task creation as a tool call
        self.log_tool_call(f"create_task_{task_data['task_type']}_{task_data['agent_name']}")
    
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
        
        # Log task execution as a tool call
        self.log_tool_call(f"execute_task_{execution_data['task_type']}_{execution_data['agent_name']}")
    
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
        
        # Log thinking process as a memory event
        self.log_memory_event("thinking_process", f"thought_{thinking_data['agent_name']}")
    
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
        
        # Log web search as a tool call
        self.log_tool_call(f"web_search_{search_data['agent_name']}")
    
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
        
        # Log file operation as a tool call
        self.log_tool_call(f"file_{file_data['operation']}_{file_data['agent_name']}")
    
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
        
        # Log iteration completion as a tool call
        self.log_tool_call(f"complete_iteration_{iteration_data['iteration_number']}_{iteration_data['agent_name']}")
    
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
        
        # Log run completion as a tool call
        self.log_tool_call(f"complete_run_{completion_data['agent_name']}")
        
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
    
    def track_agent_context(self, agent_name: str, model: str = "unknown"):
        """Context manager for tracking agent execution."""
        return AgentExecutionContext(self, agent_name, model)


class AgentExecutionContext:
    """Context manager for tracking AgentGPT agent execution."""
    
    def __init__(self, tracker: AgentGPTTracker, agent_name: str, model: str):
        self.tracker = tracker
        self.agent_name = agent_name
        self.model = model
        self.execution_id = str(uuid.uuid4())
        self.start_time = None
    
    def __enter__(self):
        """Enter the context manager - start tracking."""
        self.start_time = time.time()
        self.tracker.start_operation(self.execution_id)
        self.tracker.emit_lifecycle_event("start", 0, self.model, True, agent_name_suffix=self.agent_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager - end tracking."""
        try:
            duration_ms = self.tracker.end_operation(self.execution_id)
            tool_calls, memory_events = self.tracker.get_operation_data(self.execution_id)
            
            if exc_type is None:
                self.tracker.emit_lifecycle_event("end", duration_ms, self.model, True,
                                                agent_name_suffix=self.agent_name,
                                                tool_calls=tool_calls, memory_events=memory_events)
            else:
                self.tracker.emit_lifecycle_event("error", duration_ms, self.model, False,
                                                agent_name_suffix=self.agent_name,
                                                exception=exc_type.__name__ if exc_type else "",
                                                tool_calls=tool_calls, memory_events=memory_events)
        finally:
            self.tracker.cleanup_operation(self.execution_id)
    
    def log_tool_call(self, tool_name: str):
        """Log a tool call within this agent context."""
        self.tracker.log_tool_call(tool_name, self.execution_id)
    
    def log_memory_event(self, event_type: str, key: str):
        """Log a memory event within this agent context."""
        self.tracker.log_memory_event(event_type, key, self.execution_id)