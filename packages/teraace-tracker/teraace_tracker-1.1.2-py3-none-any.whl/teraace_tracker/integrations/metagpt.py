"""MetaGPT integration for Teraace Agentic Tracker.

MetaGPT simulates a software company via multiple specialized agents
(Product Manager, Architect, Engineer) organized via SOP-driven 
collaboration pipelines in assembly-line fashion.
"""

import time
import uuid
from typing import Any, Dict, List, Optional, Union
from functools import wraps

from .base import BaseTracker


class MetaGPTTracker(BaseTracker):
    """Tracker for MetaGPT agents and SOP workflows with team/project support."""
    
    def __init__(
        self,
        team_name: Optional[str] = None,
        sop_name: Optional[str] = None,
        project_name: Optional[str] = None,
        agent_name: Optional[str] = None,
        role: Optional[str] = None,
        session_id: Optional[str] = None,
        config=None,
        run_env: str = "local",
        **metadata
    ):
        """Initialize MetaGPT tracker with flexible team/SOP/project support."""
        # Store original parameters
        self.team_name = team_name
        self.sop_name = sop_name
        self.project_name = project_name
        self.agent_name_only = agent_name
        self.role = role
        self.metadata = metadata
        
        # Determine the primary identifier for tracking
        # Priority: sop_name > team_name > project_name
        if sop_name and (role or agent_name):
            primary_name = f"{sop_name}:{role or agent_name}"
        elif team_name and (role or agent_name):
            primary_name = f"{team_name}:{role or agent_name}"
        elif project_name and (role or agent_name):
            primary_name = f"{project_name}:{role or agent_name}"
        elif sop_name:
            primary_name = sop_name
        elif team_name:
            primary_name = team_name
        elif project_name:
            primary_name = project_name
        elif role:
            primary_name = role
        elif agent_name:
            primary_name = agent_name
        else:
            primary_name = "metagpt_agent"
        
        # Initialize base tracker
        super().__init__(
            agent_name=primary_name,
            framework_name="metagpt",
            session_id=session_id,
            config=config,
            run_env=run_env
        )
        
        # MetaGPT-specific tracking state
        self._tracked_agents = {}
        self._active_sop = None
        self._workspace_state = {}
    
    def track_agent_creation(self, agent: Any, role: str = None, **kwargs) -> None:
        """Track MetaGPT agent creation.
        
        Args:
            agent: The MetaGPT agent instance
            role: Agent role (ProductManager, Architect, Engineer, etc.)
            **kwargs: Additional agent configuration
        """
        agent_data = {
            'agent_type': agent.__class__.__name__,
            'role': role or getattr(agent, 'role', 'unknown'),
            'name': getattr(agent, 'name', 'unknown'),
            'llm_model': getattr(getattr(agent, 'llm', None), 'model', 'unknown') if hasattr(agent, 'llm') else 'unknown',
            'memory_enabled': hasattr(agent, 'memory'),
            'tools_count': len(getattr(agent, 'tools', [])),
            'profile': getattr(agent, 'profile', {}),
            'constraints': getattr(agent, 'constraints', [])
        }
        
        # Log agent creation as a tool call
        self.log_tool_call(f"create_agent_{agent_data['role']}")
        
        # Store agent for tracking
        agent_id = id(agent)
        self._tracked_agents[agent_id] = agent
    
    def track_sop_execution(self, sop: Any, agents: List[Any] = None) -> None:
        """Track SOP (Standard Operating Procedure) execution.
        
        Args:
            sop: The SOP instance
            agents: List of agents participating in the SOP
        """
        sop_data = {
            'sop_type': sop.__class__.__name__,
            'sop_name': getattr(sop, 'name', 'unknown'),
            'agent_count': len(agents) if agents else 0,
            'agent_roles': [getattr(agent, 'role', agent.__class__.__name__) for agent in (agents or [])],
            'workflow_steps': getattr(sop, 'workflow', []),
            'parallel_execution': getattr(sop, 'parallel', False)
        }
        
        # Log SOP execution as a tool call
        self.log_tool_call(f"execute_sop_{sop_data['sop_name']}")
        
        # Store SOP state
        self._active_sop = sop
    
    def track_role_execution(self, agent: Any, role: str, task: str, result: Any = None) -> None:
        """Track role-specific task execution.
        
        Args:
            agent: The agent executing the role
            role: The role being executed (PM, Architect, Engineer, etc.)
            task: The specific task being performed
            result: The result of the task execution
        """
        role_data = {
            'agent_type': agent.__class__.__name__,
            'role': role,
            'task': task,
            'task_type': type(task).__name__ if not isinstance(task, str) else 'string',
            'has_result': result is not None,
            'result_type': type(result).__name__ if result else None,
            'agent_name': getattr(agent, 'name', 'unknown')
        }
        
        # Log role execution as a tool call
        self.log_tool_call(f"{role}_{task}")
    
    def track_collaboration_step(self, from_agent: Any, to_agent: Any, message: Any, step_type: str = "handoff") -> None:
        """Track collaboration between agents in the SOP pipeline.
        
        Args:
            from_agent: Agent sending the message/work
            to_agent: Agent receiving the message/work
            message: The message or work being passed
            step_type: Type of collaboration (handoff, review, feedback)
        """
        collab_data = {
            'from_role': getattr(from_agent, 'role', from_agent.__class__.__name__),
            'to_role': getattr(to_agent, 'role', to_agent.__class__.__name__),
            'step_type': step_type,
            'message_type': type(message).__name__,
            'message_length': len(str(message)) if message else 0,
            'from_agent_name': getattr(from_agent, 'name', 'unknown'),
            'to_agent_name': getattr(to_agent, 'name', 'unknown')
        }
        
        # Log collaboration as a memory event
        self.log_memory_event("collaboration", f"{collab_data['from_role']}_to_{collab_data['to_role']}")
    
    def track_workspace_update(self, workspace: Any, update_type: str, content: Any = None) -> None:
        """Track workspace updates during SOP execution.
        
        Args:
            workspace: The workspace instance
            update_type: Type of update (document, code, design, etc.)
            content: The content being updated
        """
        workspace_data = {
            'workspace_type': workspace.__class__.__name__,
            'update_type': update_type,
            'content_type': type(content).__name__ if content else None,
            'content_size': len(str(content)) if content else 0,
            'workspace_id': getattr(workspace, 'id', 'unknown')
        }
        
        # Log workspace update as a memory event
        self.log_memory_event("workspace_update", f"{workspace_data['update_type']}")
        
        # Update workspace state
        self._workspace_state[update_type] = workspace_data
    
    def track_requirement_analysis(self, agent: Any, requirements: Any, analysis: Any = None) -> None:
        """Track requirement analysis by Product Manager.
        
        Args:
            agent: The PM agent
            requirements: Input requirements
            analysis: Analysis output
        """
        analysis_data = {
            'agent_role': getattr(agent, 'role', 'ProductManager'),
            'requirements_type': type(requirements).__name__,
            'requirements_length': len(str(requirements)) if requirements else 0,
            'has_analysis': analysis is not None,
            'analysis_type': type(analysis).__name__ if analysis else None
        }
        
        # Log requirement analysis as a tool call
        self.log_tool_call(f"analyze_requirements_{analysis_data['agent_role']}")
    
    def track_architecture_design(self, agent: Any, requirements: Any, design: Any = None) -> None:
        """Track architecture design by Architect.
        
        Args:
            agent: The architect agent
            requirements: Input requirements
            design: Architecture design output
        """
        design_data = {
            'agent_role': getattr(agent, 'role', 'Architect'),
            'requirements_type': type(requirements).__name__,
            'has_design': design is not None,
            'design_type': type(design).__name__ if design else None,
            'design_complexity': len(str(design)) if design else 0
        }
        
        # Log architecture design as a tool call
        self.log_tool_call(f"design_architecture_{design_data['agent_role']}")
    
    def track_code_generation(self, agent: Any, design: Any, code: Any = None) -> None:
        """Track code generation by Engineer.
        
        Args:
            agent: The engineer agent
            design: Input design
            code: Generated code output
        """
        code_data = {
            'agent_role': getattr(agent, 'role', 'Engineer'),
            'design_type': type(design).__name__,
            'has_code': code is not None,
            'code_type': type(code).__name__ if code else None,
            'code_length': len(str(code)) if code else 0
        }
        
        # Log code generation as a tool call
        self.log_tool_call(f"generate_code_{code_data['agent_role']}")
    
    def track_qa_testing(self, agent: Any, code: Any, test_results: Any = None) -> None:
        """Track QA testing by QA Engineer.
        
        Args:
            agent: The QA agent
            code: Code being tested
            test_results: Test results
        """
        qa_data = {
            'agent_role': getattr(agent, 'role', 'QAEngineer'),
            'code_type': type(code).__name__,
            'has_results': test_results is not None,
            'results_type': type(test_results).__name__ if test_results else None,
            'test_count': len(test_results) if isinstance(test_results, (list, dict)) else 1 if test_results else 0
        }
        
        # Log QA testing as a tool call
        self.log_tool_call(f"test_code_{qa_data['agent_role']}")
    
    def auto_track_agent(self, agent: Any, role: str = None) -> Any:
        """Automatically track a MetaGPT agent.
        
        Args:
            agent: The MetaGPT agent instance
            role: Optional role override
            
        Returns:
            The same agent (for chaining)
        """
        agent_id = id(agent)
        self._tracked_agents[agent_id] = agent
        
        # Track agent creation
        self.track_agent_creation(agent, role)
        
        return agent
    
    def extract_model_info(self, *args, **kwargs) -> str:
        """Extract model information from MetaGPT agent."""
        if args and hasattr(args[0], 'llm') and hasattr(args[0].llm, 'model'):
            return args[0].llm.model
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
    
    def track_sop_execution_context(self, sop_name: str, model: str = "unknown"):
        """Context manager for tracking SOP execution."""
        return SOPExecutionContext(self, sop_name, model)
    
    @classmethod
    def auto_track_team(cls, team_name: str, agent_roles: List[str], **tracker_kwargs):
        """
        Automatically set up tracking for a MetaGPT team with multiple agent roles.
        This is the easiest way to get started - just specify the team and roles.
        """
        trackers = {}
        for role in agent_roles:
            tracker = cls(team_name=team_name, role=role, **tracker_kwargs)
            trackers[role] = tracker
        
        return trackers if len(agent_roles) > 1 else trackers[agent_roles[0]]
    
    @classmethod
    def auto_track_sop(cls, sop_name: str, agent_roles: List[str], **tracker_kwargs):
        """
        Automatically set up tracking for a MetaGPT SOP with multiple agent roles.
        """
        trackers = {}
        for role in agent_roles:
            tracker = cls(sop_name=sop_name, role=role, **tracker_kwargs)
            trackers[role] = tracker
        
        return trackers if len(agent_roles) > 1 else trackers[agent_roles[0]]


class SOPExecutionContext:
    """Context manager for tracking MetaGPT SOP execution."""
    
    def __init__(self, tracker: MetaGPTTracker, sop_name: str, model: str):
        self.tracker = tracker
        self.sop_name = sop_name
        self.model = model
        self.execution_id = str(uuid.uuid4())
        self.start_time = None
    
    def __enter__(self):
        """Enter the context manager - start tracking."""
        self.start_time = time.time()
        self.tracker.start_operation(self.execution_id)
        self.tracker.emit_lifecycle_event("start", 0, self.model, True, agent_name_suffix=self.sop_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager - end tracking."""
        try:
            duration_ms = self.tracker.end_operation(self.execution_id)
            tool_calls, memory_events = self.tracker.get_operation_data(self.execution_id)
            
            if exc_type is None:
                self.tracker.emit_lifecycle_event("end", duration_ms, self.model, True,
                                                agent_name_suffix=self.sop_name,
                                                tool_calls=tool_calls, memory_events=memory_events)
            else:
                self.tracker.emit_lifecycle_event("error", duration_ms, self.model, False,
                                                agent_name_suffix=self.sop_name,
                                                exception=exc_type.__name__ if exc_type else "",
                                                tool_calls=tool_calls, memory_events=memory_events)
        finally:
            self.tracker.cleanup_operation(self.execution_id)
    
    def log_tool_call(self, tool_name: str):
        """Log a tool call within this SOP context."""
        self.tracker.log_tool_call(tool_name, self.execution_id)
    
    def log_memory_event(self, event_type: str, key: str):
        """Log a memory event within this SOP context."""
        self.tracker.log_memory_event(event_type, key, self.execution_id)