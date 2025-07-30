"""PhiData integration for Teraace Agentic Tracker.

PhiData allows defining workflows composed of multiple agent instances,
capable of memory-sharing, tool usage, reasoning, team orchestration,
and UI-based multi-agent interaction.
"""

import time
import uuid
from typing import Any, Dict, List, Optional, Union
from functools import wraps

from .base import BaseTracker


class PhiDataTracker(BaseTracker):
    """Tracker for PhiData agents and workflows with comprehensive multi-agent support."""
    
    def __init__(
        self,
        workflow_name: Optional[str] = None,
        agent_name: Optional[str] = None,
        session_id: Optional[str] = None,
        config=None,
        run_env: str = "local",
        **metadata
    ):
        """Initialize PhiData tracker with flexible workflow/agent support."""
        # Store original parameters
        self.workflow_name = workflow_name
        self.agent_name_only = agent_name
        self.metadata = metadata
        
        # Determine the primary identifier for tracking
        if workflow_name and agent_name:
            primary_name = f"{workflow_name}:{agent_name}"
        elif workflow_name:
            primary_name = workflow_name
        elif agent_name:
            primary_name = agent_name
        else:
            primary_name = "phidata_workflow"
        
        # Initialize base tracker
        super().__init__(
            agent_name=primary_name,
            framework_name="phidata",
            session_id=session_id,
            config=config,
            run_env=run_env
        )
        
        # PhiData-specific tracking state
        self._tracked_agents = {}
        self._tracked_workflows = {}
        self._session_states = {}
    
    def track_agent_creation(self, agent: Any, tools: List[Any] = None, **kwargs) -> None:
        """Track PhiData agent creation.
        
        Args:
            agent: The PhiData agent instance
            tools: List of tools available to the agent
            **kwargs: Additional agent configuration
        """
        agent_data = {
            'agent_type': agent.__class__.__name__,
            'agent_name': getattr(agent, 'name', 'unknown'),
            'llm_model': getattr(getattr(agent, 'llm', None), 'model', 'unknown') if hasattr(agent, 'llm') else 'unknown',
            'tool_count': len(tools) if tools else 0,
            'tool_names': [getattr(tool, 'name', tool.__class__.__name__) for tool in (tools or [])],
            'has_memory': hasattr(agent, 'memory'),
            'has_knowledge': hasattr(agent, 'knowledge'),
            'has_storage': hasattr(agent, 'storage'),
            'system_prompt': getattr(agent, 'system_prompt', ''),
            'instructions': getattr(agent, 'instructions', []),
            'show_tool_calls': kwargs.get('show_tool_calls', False),
            'markdown': kwargs.get('markdown', False)
        }
        
        # Log agent creation as a tool call
        self.log_tool_call(f"create_agent_{agent_data['agent_name']}")
        
        # Store agent for tracking
        agent_id = id(agent)
        self._tracked_agents[agent_id] = agent
    
    def track_workflow_creation(self, workflow: Any, agents: List[Any] = None, **kwargs) -> None:
        """Track PhiData workflow creation.
        
        Args:
            workflow: The workflow instance
            agents: List of agents in the workflow
            **kwargs: Additional workflow configuration
        """
        workflow_data = {
            'workflow_type': workflow.__class__.__name__,
            'workflow_name': getattr(workflow, 'name', 'unknown'),
            'agent_count': len(agents) if agents else 0,
            'agent_names': [getattr(agent, 'name', agent.__class__.__name__) for agent in (agents or [])],
            'has_session_state': hasattr(workflow, 'session_state'),
            'has_ui': hasattr(workflow, 'ui'),
            'debug_mode': kwargs.get('debug', False),
            'session_id': getattr(workflow, 'session_id', None)
        }
        
        # Log workflow creation as a tool call
        self.log_tool_call(f"create_workflow_{workflow_data['workflow_name']}")
        
        # Store workflow for tracking
        workflow_id = id(workflow)
        self._tracked_workflows[workflow_id] = workflow
    
    def track_agent_execution(self, agent: Any, message: str, response: Any = None, **kwargs) -> None:
        """Track agent execution.
        
        Args:
            agent: The agent executing
            message: Input message
            response: Agent response
            **kwargs: Additional execution parameters
        """
        execution_data = {
            'agent_type': agent.__class__.__name__,
            'agent_name': getattr(agent, 'name', 'unknown'),
            'message_length': len(message) if message else 0,
            'has_response': response is not None,
            'response_type': type(response).__name__ if response else None,
            'response_length': len(str(response)) if response else 0,
            'stream': kwargs.get('stream', False),
            'session_id': kwargs.get('session_id')
        }
        
        # Log agent execution as a tool call
        self.log_tool_call(f"execute_{execution_data['agent_name']}")
    
    def track_workflow_execution(self, workflow: Any, message: str, response: Any = None, **kwargs) -> None:
        """Track workflow execution.
        
        Args:
            workflow: The workflow executing
            message: Input message
            response: Workflow response
            **kwargs: Additional execution parameters
        """
        execution_data = {
            'workflow_type': workflow.__class__.__name__,
            'workflow_name': getattr(workflow, 'name', 'unknown'),
            'message_length': len(message) if message else 0,
            'has_response': response is not None,
            'response_type': type(response).__name__ if response else None,
            'response_length': len(str(response)) if response else 0,
            'agent_count': len(getattr(workflow, 'agents', [])),
            'session_id': kwargs.get('session_id')
        }
        
        # Log workflow execution as a tool call
        self.log_tool_call(f"execute_workflow_{execution_data['workflow_name']}")
    
    def track_tool_execution(self, agent: Any, tool: Any, input_data: Any, output_data: Any = None) -> None:
        """Track tool execution by agent.
        
        Args:
            agent: The agent using the tool
            tool: The tool being executed
            input_data: Input data to the tool
            output_data: Output from the tool
        """
        tool_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'tool_name': getattr(tool, 'name', tool.__class__.__name__),
            'tool_type': tool.__class__.__name__,
            'tool_description': getattr(tool, 'description', ''),
            'input_type': type(input_data).__name__,
            'has_output': output_data is not None,
            'output_type': type(output_data).__name__ if output_data else None,
            'output_length': len(str(output_data)) if output_data else 0
        }
        
        # Log tool execution as a tool call
        self.log_tool_call(f"{tool_data['tool_name']}_{tool_data['agent_name']}")
    
    def track_memory_operation(self, agent: Any, operation: str, data: Any = None, **kwargs) -> None:
        """Track memory operations.
        
        Args:
            agent: The agent performing memory operation
            operation: Type of operation (add, get, search, clear)
            data: Memory data
            **kwargs: Additional memory parameters
        """
        memory_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'operation': operation,
            'has_data': data is not None,
            'data_type': type(data).__name__ if data else None,
            'data_size': len(str(data)) if data else 0,
            'memory_type': kwargs.get('memory_type', 'unknown')
        }
        
        # Log memory operation as a memory event
        self.log_memory_event("memory_operation", f"{memory_data['operation']}_{memory_data['agent_name']}")
    
    def track_knowledge_operation(self, agent: Any, operation: str, query: str = None, results: Any = None) -> None:
        """Track knowledge base operations.
        
        Args:
            agent: The agent using knowledge
            operation: Type of operation (search, add, update)
            query: Search query
            results: Operation results
        """
        knowledge_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'operation': operation,
            'query': query,
            'query_length': len(query) if query else 0,
            'has_results': results is not None,
            'results_type': type(results).__name__ if results else None,
            'results_count': len(results) if isinstance(results, (list, dict)) else 1 if results else 0
        }
        
        # Log knowledge operation as a memory event
        self.log_memory_event("knowledge_operation", f"{knowledge_data['operation']}_{knowledge_data['agent_name']}")
    
    def track_session_state(self, workflow: Any, state_key: str, state_value: Any, operation: str = "update") -> None:
        """Track session state changes.
        
        Args:
            workflow: The workflow managing session state
            state_key: State key
            state_value: State value
            operation: Type of operation (get, set, update, delete)
        """
        state_data = {
            'workflow_name': getattr(workflow, 'name', 'unknown'),
            'state_key': state_key,
            'operation': operation,
            'value_type': type(state_value).__name__ if state_value else None,
            'value_size': len(str(state_value)) if state_value else 0,
            'session_id': getattr(workflow, 'session_id', 'unknown')
        }
        
        # Log session state as a memory event
        self.log_memory_event("session_state", f"{state_data['operation']}_{state_data['state_key']}")
        
        # Update tracked session state
        workflow_id = id(workflow)
        if workflow_id not in self._session_states:
            self._session_states[workflow_id] = {}
        self._session_states[workflow_id][state_key] = state_value
    
    def track_ui_interaction(self, workflow: Any, interaction_type: str, data: Any = None) -> None:
        """Track UI interactions in PhiData workflows.
        
        Args:
            workflow: The workflow with UI
            interaction_type: Type of interaction (input, output, button_click, etc.)
            data: Interaction data
        """
        ui_data = {
            'workflow_name': getattr(workflow, 'name', 'unknown'),
            'interaction_type': interaction_type,
            'has_data': data is not None,
            'data_type': type(data).__name__ if data else None,
            'data_size': len(str(data)) if data else 0,
            'session_id': getattr(workflow, 'session_id', 'unknown')
        }
        
        # Log UI interaction as a memory event
        self.log_memory_event("ui_interaction", f"{ui_data['interaction_type']}_{ui_data['workflow_name']}")
    
    def track_agent_reasoning(self, agent: Any, reasoning_step: str, thought: str, action: str = None) -> None:
        """Track agent reasoning steps.
        
        Args:
            agent: The reasoning agent
            reasoning_step: Step in reasoning process
            thought: Agent's thought
            action: Action taken (if any)
        """
        reasoning_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'reasoning_step': reasoning_step,
            'thought': thought,
            'thought_length': len(thought) if thought else 0,
            'action': action,
            'has_action': action is not None
        }
        
        # Log reasoning as a memory event
        self.log_memory_event("reasoning", f"{reasoning_data['reasoning_step']}_{reasoning_data['agent_name']}")
    
    def track_team_coordination(self, workflow: Any, coordinator_agent: Any, target_agents: List[Any], task: str) -> None:
        """Track team coordination in multi-agent workflows.
        
        Args:
            workflow: The workflow managing coordination
            coordinator_agent: Agent coordinating the team
            target_agents: Agents being coordinated
            task: Task being coordinated
        """
        coordination_data = {
            'workflow_name': getattr(workflow, 'name', 'unknown'),
            'coordinator_name': getattr(coordinator_agent, 'name', 'unknown'),
            'target_count': len(target_agents),
            'target_names': [getattr(agent, 'name', agent.__class__.__name__) for agent in target_agents],
            'task': task,
            'task_length': len(task) if task else 0
        }
        
        # Log coordination as a memory event
        self.log_memory_event("team_coordination", f"{coordination_data['coordinator_name']}_{coordination_data['task']}")
    
    def auto_track_agent(self, agent: Any, tools: List[Any] = None) -> Any:
        """Automatically track a PhiData agent.
        
        Args:
            agent: The PhiData agent instance
            tools: Optional list of tools
            
        Returns:
            The same agent (for chaining)
        """
        agent_id = id(agent)
        self._tracked_agents[agent_id] = agent
        
        # Track agent creation
        self.track_agent_creation(agent, tools)
        
        return agent
    
    def auto_track_workflow(self, workflow: Any, agents: List[Any] = None) -> Any:
        """Automatically track a PhiData workflow.
        
        Args:
            workflow: The workflow instance
            agents: Optional list of agents in workflow
            
        Returns:
            The same workflow (for chaining)
        """
        workflow_id = id(workflow)
        self._tracked_workflows[workflow_id] = workflow
        
        # Track workflow creation
        self.track_workflow_creation(workflow, agents)
        
        return workflow
    
    def extract_model_info(self, *args, **kwargs) -> str:
        """Extract model information from PhiData agent."""
        if args and hasattr(args[0], 'llm') and hasattr(args[0].llm, 'model'):
            return args[0].llm.model
        return kwargs.get('model', 'gpt-4')
    
    def track_agent_execution_decorator(self, func):
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
    
    def track_workflow_context(self, workflow_name: str, model: str = "unknown"):
        """Context manager for tracking workflow execution."""
        return WorkflowExecutionContext(self, workflow_name, model)
    
    @classmethod
    def auto_track_workflow_with_agents(cls, workflow_name: str, agent_names: List[str], **tracker_kwargs):
        """
        Automatically set up tracking for a PhiData workflow with multiple agents.
        This is the easiest way to get started - just specify the workflow and agent names.
        """
        trackers = {}
        for agent_name in agent_names:
            tracker = cls(workflow_name=workflow_name, agent_name=agent_name, **tracker_kwargs)
            trackers[agent_name] = tracker
        
        return trackers if len(agent_names) > 1 else trackers[agent_names[0]]
    
    @classmethod
    def auto_track_team_workflow(cls, workflow_obj, **tracker_kwargs):
        """
        Automatically set up tracking for a PhiData workflow object.
        This wraps the workflow's run method with tracking.
        """
        workflow_name = getattr(workflow_obj, 'name', workflow_obj.__class__.__name__)
        tracker = cls(workflow_name=workflow_name, **tracker_kwargs)
        
        # Wrap the run method if it exists
        if hasattr(workflow_obj, 'run'):
            original_run = workflow_obj.run
            
            @tracker.track_agent_execution_decorator
            def tracked_run(*args, **kwargs):
                return original_run(*args, **kwargs)
            
            workflow_obj.run = tracked_run
        
        # Store tracker reference
        workflow_obj._teraace_tracker = tracker
        
        return workflow_obj


class WorkflowExecutionContext:
    """Context manager for tracking PhiData workflow execution."""
    
    def __init__(self, tracker: PhiDataTracker, workflow_name: str, model: str):
        self.tracker = tracker
        self.workflow_name = workflow_name
        self.model = model
        self.execution_id = str(uuid.uuid4())
        self.start_time = None
    
    def __enter__(self):
        """Enter the context manager - start tracking."""
        self.start_time = time.time()
        self.tracker.start_operation(self.execution_id)
        self.tracker.emit_lifecycle_event("start", 0, self.model, True, agent_name_suffix=self.workflow_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager - end tracking."""
        try:
            duration_ms = self.tracker.end_operation(self.execution_id)
            tool_calls, memory_events = self.tracker.get_operation_data(self.execution_id)
            
            if exc_type is None:
                self.tracker.emit_lifecycle_event("end", duration_ms, self.model, True,
                                                agent_name_suffix=self.workflow_name,
                                                tool_calls=tool_calls, memory_events=memory_events)
            else:
                self.tracker.emit_lifecycle_event("error", duration_ms, self.model, False,
                                                agent_name_suffix=self.workflow_name,
                                                exception=exc_type.__name__ if exc_type else "",
                                                tool_calls=tool_calls, memory_events=memory_events)
        finally:
            self.tracker.cleanup_operation(self.execution_id)
    
    def log_tool_call(self, tool_name: str):
        """Log a tool call within this workflow context."""
        self.tracker.log_tool_call(tool_name, self.execution_id)
    
    def log_memory_event(self, event_type: str, key: str):
        """Log a memory event within this workflow context."""
        self.tracker.log_memory_event(event_type, key, self.execution_id)