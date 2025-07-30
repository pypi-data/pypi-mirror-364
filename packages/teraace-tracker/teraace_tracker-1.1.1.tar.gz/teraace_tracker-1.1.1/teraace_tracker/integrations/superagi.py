"""SuperAGI integration for Teraace Agentic Tracker.

SuperAGI is designed to spawn, manage, and run multiple concurrent autonomous agents,
with tooling, workflows, dashboards, telemetry, and agent coordination support.
"""

import time
import uuid
from typing import Any, Dict, List, Optional, Union
from functools import wraps

from .base import BaseTracker


class SuperAGITracker(BaseTracker):
    """Tracker for SuperAGI autonomous agents with multi-agent project support."""
    
    def __init__(
        self,
        project_name: Optional[str] = None,
        workflow_name: Optional[str] = None,
        agent_name: Optional[str] = None,
        session_id: Optional[str] = None,
        config=None,
        run_env: str = "local",
        **metadata
    ):
        """Initialize SuperAGI tracker with flexible project/workflow/agent support."""
        # Store original parameters
        self.project_name = project_name
        self.workflow_name = workflow_name
        self.agent_name_only = agent_name
        self.metadata = metadata
        
        # Determine the primary identifier for tracking
        # Priority: project_name > workflow_name > agent_name
        if project_name and agent_name:
            primary_name = f"{project_name}:{agent_name}"
        elif workflow_name and agent_name:
            primary_name = f"{workflow_name}:{agent_name}"
        elif project_name:
            primary_name = project_name
        elif workflow_name:
            primary_name = workflow_name
        elif agent_name:
            primary_name = agent_name
        else:
            primary_name = "superagi_agent"
        
        # Initialize base tracker
        super().__init__(
            agent_name=primary_name,
            framework_name="superagi",
            session_id=session_id,
            config=config,
            run_env=run_env
        )
        
        # SuperAGI-specific tracking state
        self._tracked_agents = {}
        self._active_runs = {}
        self._concurrent_agents = {}
        self._project_state = {}
    
    def track_agent_creation(self, agent: Any, agent_config: Dict[str, Any] = None, **kwargs) -> None:
        """Track SuperAGI agent creation with project context.
        
        Args:
            agent: The SuperAGI agent instance
            agent_config: Configuration used to create the agent
            **kwargs: Additional agent parameters
        """
        config = agent_config or {}
        agent_data = {
            'agent_name': config.get('name', getattr(agent, 'name', 'unknown')),
            'agent_description': config.get('description', getattr(agent, 'description', '')),
            'model': config.get('model', getattr(agent, 'model', 'gpt-4')),
            'max_iterations': config.get('max_iterations', getattr(agent, 'max_iterations', 25)),
            'tools': config.get('tools', getattr(agent, 'tools', [])),
            'tool_count': len(config.get('tools', getattr(agent, 'tools', []))),
            'agent_workflow': config.get('agent_workflow', getattr(agent, 'agent_workflow', 'Goal Based Agent')),
            'permission_type': config.get('permission_type', getattr(agent, 'permission_type', 'God Mode')),
            'project_name': self.project_name,
            'workflow_name': self.workflow_name,
            'concurrent_capable': kwargs.get('concurrent_capable', True),
            'resource_manager': hasattr(agent, 'resource_manager'),
            'telemetry_enabled': kwargs.get('telemetry_enabled', True)
        }
        
        # Log agent creation as a tool call
        self.log_tool_call(f"create_agent_{agent_data['agent_name']}")
        
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
            'run_id': run_id or str(uuid.uuid4()),
            'primary_goal': goals[0] if goals else '',
            'start_timestamp': getattr(agent, 'start_time', time.time()),
            'project_name': self.project_name,
            'workflow_name': self.workflow_name
        }
        
        # Log run start as a tool call
        self.log_tool_call(f"start_run_{run_data['agent_name']}")
        
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
            'execution_successful': not isinstance(tool_output, Exception),
            'project_name': self.project_name,
            'workflow_name': self.workflow_name
        }
        
        # Log tool execution as a tool call
        self.log_tool_call(f"{tool_data['tool_name']}_{tool_data['agent_name']}")
    
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
            'has_error': bool(step_result.get('error')),
            'project_name': self.project_name,
            'workflow_name': self.workflow_name
        }
        
        # Log step execution as a tool call
        self.log_tool_call(f"execute_step_{step_data['step_type']}_{step_data['agent_name']}")
    
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
            'creation_timestamp': resource.get('created_at'),
            'project_name': self.project_name,
            'workflow_name': self.workflow_name
        }
        
        # Log resource creation as a memory event
        self.log_memory_event("resource_creation", f"{resource_data['resource_type']}_{resource_data['resource_name']}")
    
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
            'update_timestamp': knowledge_data.get('timestamp'),
            'project_name': self.project_name,
            'workflow_name': self.workflow_name
        }
        
        # Log knowledge update as a memory event
        self.log_memory_event("knowledge_update", f"{knowledge_update_data['knowledge_type']}_{knowledge_update_data['agent_name']}")
    
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
            'thoughts_length': len(thoughts.get('thoughts', '')),
            'project_name': self.project_name,
            'workflow_name': self.workflow_name
        }
        
        # Log agent thinking as a memory event
        self.log_memory_event("agent_thinking", f"reasoning_{thinking_data['agent_name']}")
    
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
            'iteration_status': iteration_summary.get('status', 'completed'),
            'project_name': self.project_name,
            'workflow_name': self.workflow_name
        }
        
        # Log iteration completion as a tool call
        self.log_tool_call(f"complete_iteration_{iteration_data['iteration_number']}_{iteration_data['agent_name']}")
    
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
            'run_duration': run_summary.get('duration'),
            'project_name': self.project_name,
            'workflow_name': self.workflow_name
        }
        
        # Log run completion as a tool call
        self.log_tool_call(f"complete_run_{completion_data['agent_name']}")
        
        # Clean up run tracking
        if run_id in self._active_runs:
            del self._active_runs[run_id]
    
    def track_concurrent_agents(self, agents: List[Any], coordination_type: str = "parallel") -> None:
        """Track multiple concurrent agents in SuperAGI.
        
        Args:
            agents: List of concurrent agents
            coordination_type: Type of coordination (parallel, sequential, competitive)
        """
        concurrent_data = {
            'agent_count': len(agents),
            'agent_names': [getattr(agent, 'name', f'agent_{i}') for i, agent in enumerate(agents)],
            'coordination_type': coordination_type,
            'project_name': self.project_name,
            'workflow_name': self.workflow_name,
            'concurrent_session_id': str(uuid.uuid4())
        }
        
        # Log concurrent agent coordination as a memory event
        self.log_memory_event("concurrent_coordination", f"{coordination_type}_{len(agents)}_agents")
        
        # Store concurrent agents
        for agent in agents:
            agent_id = id(agent)
            self._concurrent_agents[agent_id] = {
                'agent': agent,
                'coordination_type': coordination_type,
                'session_id': concurrent_data['concurrent_session_id']
            }
    
    def track_agent_coordination(self, coordinator_agent: Any, target_agents: List[Any], task: str) -> None:
        """Track agent coordination in multi-agent projects.
        
        Args:
            coordinator_agent: The agent coordinating others
            target_agents: Agents being coordinated
            task: The coordination task
        """
        coordination_data = {
            'coordinator_name': getattr(coordinator_agent, 'name', 'unknown'),
            'target_count': len(target_agents),
            'target_names': [getattr(agent, 'name', f'agent_{i}') for i, agent in enumerate(target_agents)],
            'task': task,
            'project_name': self.project_name,
            'workflow_name': self.workflow_name
        }
        
        # Log coordination as a memory event
        self.log_memory_event("agent_coordination", f"{coordination_data['coordinator_name']}_{task}")
    
    def track_project_state_update(self, state_key: str, state_value: Any, agent: Any = None) -> None:
        """Track project state updates across multiple agents.
        
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
            'project_name': self.project_name,
            'workflow_name': self.workflow_name,
            'timestamp': time.time()
        }
        
        # Update project state
        self._project_state[state_key] = state_value
        
        # Log state update as a memory event
        self.log_memory_event("project_state", f"update_{state_key}")
    
    def track_telemetry_data(self, agent: Any, telemetry: Dict[str, Any]) -> None:
        """Track telemetry data from SuperAGI agents.
        
        Args:
            agent: The agent generating telemetry
            telemetry: Telemetry data
        """
        telemetry_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'metrics': list(telemetry.keys()),
            'metric_count': len(telemetry),
            'cpu_usage': telemetry.get('cpu_usage', 0),
            'memory_usage': telemetry.get('memory_usage', 0),
            'execution_time': telemetry.get('execution_time', 0),
            'project_name': self.project_name,
            'workflow_name': self.workflow_name
        }
        
        # Log telemetry as a memory event
        self.log_memory_event("telemetry", f"metrics_{telemetry_data['agent_name']}")
    
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
    
    def track_project_context(self, project_name: str, model: str = "unknown"):
        """Context manager for tracking project execution."""
        return ProjectExecutionContext(self, project_name, model)
    
    @classmethod
    def auto_track_project(cls, project_name: str, agent_names: List[str], **tracker_kwargs):
        """
        Automatically set up tracking for a SuperAGI project with multiple agents.
        This is the easiest way to get started - just specify the project and agent names.
        """
        trackers = {}
        for agent_name in agent_names:
            tracker = cls(project_name=project_name, agent_name=agent_name, **tracker_kwargs)
            trackers[agent_name] = tracker
        
        return trackers if len(agent_names) > 1 else trackers[agent_names[0]]
    
    @classmethod
    def auto_track_workflow(cls, workflow_name: str, agent_names: List[str], **tracker_kwargs):
        """
        Automatically set up tracking for a SuperAGI workflow with multiple agents.
        """
        trackers = {}
        for agent_name in agent_names:
            tracker = cls(workflow_name=workflow_name, agent_name=agent_name, **tracker_kwargs)
            trackers[agent_name] = tracker
        
        return trackers if len(agent_names) > 1 else trackers[agent_names[0]]


class ProjectExecutionContext:
    """Context manager for tracking SuperAGI project execution."""
    
    def __init__(self, tracker: SuperAGITracker, project_name: str, model: str):
        self.tracker = tracker
        self.project_name = project_name
        self.model = model
        self.execution_id = str(uuid.uuid4())
        self.start_time = None
    
    def __enter__(self):
        """Enter the context manager - start tracking."""
        self.start_time = time.time()
        self.tracker.start_operation(self.execution_id)
        self.tracker.emit_lifecycle_event("start", 0, self.model, True, agent_name_suffix=self.project_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager - end tracking."""
        try:
            duration_ms = self.tracker.end_operation(self.execution_id)
            tool_calls, memory_events = self.tracker.get_operation_data(self.execution_id)
            
            if exc_type is None:
                self.tracker.emit_lifecycle_event("end", duration_ms, self.model, True,
                                                agent_name_suffix=self.project_name,
                                                tool_calls=tool_calls, memory_events=memory_events)
            else:
                self.tracker.emit_lifecycle_event("error", duration_ms, self.model, False,
                                                agent_name_suffix=self.project_name,
                                                exception=exc_type.__name__ if exc_type else "",
                                                tool_calls=tool_calls, memory_events=memory_events)
        finally:
            self.tracker.cleanup_operation(self.execution_id)
    
    def log_tool_call(self, tool_name: str):
        """Log a tool call within this project context."""
        self.tracker.log_tool_call(tool_name, self.execution_id)
    
    def log_memory_event(self, event_type: str, key: str):
        """Log a memory event within this project context."""
        self.tracker.log_memory_event(event_type, key, self.execution_id)