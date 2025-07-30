"""Mirascope integration for Teraace Agentic Tracker.

Mirascope supports building autonomous or multi-agent systems where agents
can use tools, memory, state, and be coordinated in higher-level workflows.
"""

import time
import uuid
from typing import Any, Dict, List, Optional, Union
from functools import wraps

from .base import BaseTracker


class MirascopeTracker(BaseTracker):
    """Tracker for Mirascope agents and workflows with multi-agent support."""
    
    def __init__(
        self,
        workflow_name: Optional[str] = None,
        agent_name: Optional[str] = None,
        session_id: Optional[str] = None,
        config=None,
        run_env: str = "local",
        **metadata
    ):
        """Initialize Mirascope tracker with flexible workflow/agent support."""
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
            primary_name = "mirascope_agent"
        
        # Initialize base tracker
        super().__init__(
            agent_name=primary_name,
            framework_name="mirascope",
            session_id=session_id,
            config=config,
            run_env=run_env
        )
        
        # Mirascope-specific tracking state
        self._tracked_agents = {}
        self._active_workflows = {}
        self._agent_states = {}
    
    def track_agent_creation(self, agent: Any, tools: List[Any] = None, **kwargs) -> None:
        """Track Mirascope agent creation.
        
        Args:
            agent: The Mirascope agent instance
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
            'has_state': hasattr(agent, 'state'),
            'system_prompt': getattr(agent, 'system_prompt', ''),
            'temperature': kwargs.get('temperature', 0.7)
        }
        
        # Log agent creation as a tool call
        self.log_tool_call(f"create_agent_{agent_data['agent_name']}")
        
        # Store agent for tracking
        agent_id = id(agent)
        self._tracked_agents[agent_id] = agent
    
    def track_agent_execution(self, agent: Any, input_data: Any, response: Any = None) -> None:
        """Track agent execution.
        
        Args:
            agent: The agent executing
            input_data: Input data/prompt
            response: Agent response
        """
        execution_data = {
            'agent_type': agent.__class__.__name__,
            'agent_name': getattr(agent, 'name', 'unknown'),
            'input_type': type(input_data).__name__,
            'input_length': len(str(input_data)) if input_data else 0,
            'has_response': response is not None,
            'response_type': type(response).__name__ if response else None,
            'response_length': len(str(response)) if response else 0
        }
        
        # Log agent execution as a tool call
        self.log_tool_call(f"execute_{execution_data['agent_name']}")
    
    def track_tool_usage(self, agent: Any, tool: Any, input_data: Any, output_data: Any = None) -> None:
        """Track tool usage by agent.
        
        Args:
            agent: The agent using the tool
            tool: The tool being used
            input_data: Input to the tool
            output_data: Output from the tool
        """
        tool_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'tool_name': getattr(tool, 'name', tool.__class__.__name__),
            'tool_type': tool.__class__.__name__,
            'tool_description': getattr(tool, 'description', ''),
            'input_type': type(input_data).__name__,
            'has_output': output_data is not None,
            'output_type': type(output_data).__name__ if output_data else None
        }
        
        # Log tool usage as a tool call
        self.log_tool_call(f"{tool_data['tool_name']}_{tool_data['agent_name']}")
    
    def track_memory_operation(self, agent: Any, operation: str, key: str = None, value: Any = None) -> None:
        """Track memory operations.
        
        Args:
            agent: The agent performing memory operation
            operation: Type of operation (store, retrieve, update, delete)
            key: Memory key
            value: Memory value
        """
        memory_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'operation': operation,
            'key': key,
            'has_value': value is not None,
            'value_type': type(value).__name__ if value else None,
            'value_size': len(str(value)) if value else 0
        }
        
        # Log memory operation as a memory event
        self.log_memory_event("memory_operation", f"{memory_data['operation']}_{memory_data['agent_name']}")
    
    def track_state_change(self, agent: Any, old_state: Any, new_state: Any) -> None:
        """Track agent state changes.
        
        Args:
            agent: The agent whose state changed
            old_state: Previous state
            new_state: New state
        """
        state_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'old_state_type': type(old_state).__name__ if old_state else None,
            'new_state_type': type(new_state).__name__ if new_state else None,
            'state_changed': old_state != new_state
        }
        
        # Log state change as a memory event
        self.log_memory_event("state_change", f"{state_data['agent_name']}")
        
        # Update tracked state
        agent_id = id(agent)
        self._agent_states[agent_id] = new_state
    
    def track_workflow_execution(self, workflow: Any, agents: List[Any] = None) -> None:
        """Track workflow execution with multiple agents.
        
        Args:
            workflow: The workflow instance
            agents: List of agents in the workflow
        """
        workflow_data = {
            'workflow_type': workflow.__class__.__name__,
            'workflow_name': getattr(workflow, 'name', 'unknown'),
            'agent_count': len(agents) if agents else 0,
            'agent_names': [getattr(agent, 'name', agent.__class__.__name__) for agent in (agents or [])],
            'parallel_execution': getattr(workflow, 'parallel', False),
            'workflow_steps': getattr(workflow, 'steps', [])
        }
        
        # Log workflow execution as a tool call
        self.log_tool_call(f"execute_workflow_{workflow_data['workflow_name']}")
        
        # Store workflow
        workflow_id = id(workflow)
        self._active_workflows[workflow_id] = workflow
    
    def track_agent_coordination(self, coordinator: Any, agents: List[Any], task: str) -> None:
        """Track agent coordination in multi-agent workflows.
        
        Args:
            coordinator: The coordinating agent or system
            agents: List of agents being coordinated
            task: The task being coordinated
        """
        coordination_data = {
            'coordinator_type': coordinator.__class__.__name__,
            'coordinator_name': getattr(coordinator, 'name', 'unknown'),
            'agent_count': len(agents),
            'agent_names': [getattr(agent, 'name', agent.__class__.__name__) for agent in agents],
            'task': task,
            'task_type': type(task).__name__
        }
        
        # Log coordination as a memory event
        self.log_memory_event("coordination", f"{coordination_data['coordinator_name']}_{coordination_data['task']}")
    
    def track_response_generation(self, agent: Any, prompt: str, response: Any, model_info: Dict = None) -> None:
        """Track response generation by agent.
        
        Args:
            agent: The agent generating response
            prompt: Input prompt
            response: Generated response
            model_info: Model information and parameters
        """
        response_data = {
            'agent_name': getattr(agent, 'name', 'unknown'),
            'prompt_length': len(prompt) if prompt else 0,
            'response_length': len(str(response)) if response else 0,
            'model': model_info.get('model', 'unknown') if model_info else 'unknown',
            'temperature': model_info.get('temperature', 0.7) if model_info else 0.7,
            'max_tokens': model_info.get('max_tokens') if model_info else None
        }
        
        # Log response generation as a tool call
        self.log_tool_call(f"generate_response_{response_data['agent_name']}")
    
    def track_chain_execution(self, chain: Any, agents: List[Any], input_data: Any, output_data: Any = None) -> None:
        """Track chain execution with multiple agents.
        
        Args:
            chain: The chain instance
            agents: Agents in the chain
            input_data: Input to the chain
            output_data: Output from the chain
        """
        chain_data = {
            'chain_type': chain.__class__.__name__,
            'chain_name': getattr(chain, 'name', 'unknown'),
            'agent_count': len(agents),
            'agent_sequence': [getattr(agent, 'name', agent.__class__.__name__) for agent in agents],
            'input_type': type(input_data).__name__,
            'has_output': output_data is not None,
            'output_type': type(output_data).__name__ if output_data else None
        }
        
        # Log chain execution as a tool call
        self.log_tool_call(f"execute_chain_{chain_data['chain_name']}")
    
    def auto_track_agent(self, agent: Any, tools: List[Any] = None) -> Any:
        """Automatically track a Mirascope agent.
        
        Args:
            agent: The Mirascope agent instance
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
        """Automatically track a Mirascope workflow.
        
        Args:
            workflow: The workflow instance
            agents: Optional list of agents in workflow
            
        Returns:
            The same workflow (for chaining)
        """
        workflow_id = id(workflow)
        self._active_workflows[workflow_id] = workflow
        
        # Track workflow execution
        self.track_workflow_execution(workflow, agents)
        
        return workflow
    
    def extract_model_info(self, *args, **kwargs) -> str:
        """Extract model information from Mirascope agent."""
        if args and hasattr(args[0], 'llm') and hasattr(args[0].llm, 'model'):
            return args[0].llm.model
        return kwargs.get('model', 'gpt-3.5-turbo')
    
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
        Automatically set up tracking for a Mirascope workflow with multiple agents.
        This is the easiest way to get started - just specify the workflow and agent names.
        """
        trackers = {}
        for agent_name in agent_names:
            tracker = cls(workflow_name=workflow_name, agent_name=agent_name, **tracker_kwargs)
            trackers[agent_name] = tracker
        
        return trackers if len(agent_names) > 1 else trackers[agent_names[0]]


class WorkflowExecutionContext:
    """Context manager for tracking Mirascope workflow execution."""
    
    def __init__(self, tracker: MirascopeTracker, workflow_name: str, model: str):
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