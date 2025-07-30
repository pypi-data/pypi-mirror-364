"""
CrewAI integration for Teraace tracker - Extensible Multi-Agent Support

This tracker supports both single agents and multi-agent swarms with minimal setup.
Key features:
- Auto-tracking with one line of code
- Flexible naming (crew_name, agent_name, or both)
- Backwards compatible with existing single-agent setups
- Extensible metadata support
"""

import time
import uuid
from typing import Dict, List, Optional
from functools import wraps

from .base import BaseTracker


class CrewAITracker(BaseTracker):
    """CrewAI integration for tracking agent and task events with multi-agent support."""
    
    def __init__(
        self,
        crew_name: Optional[str] = None,
        agent_name: Optional[str] = None,
        session_id: Optional[str] = None,
        config=None,
        run_env: str = "local",
        **metadata
    ):
        """Initialize CrewAI tracker with flexible agent/crew support."""
        # Store original parameters
        self.crew_name = crew_name
        self.agent_name_only = agent_name
        self.metadata = metadata
        
        # Determine the primary identifier for tracking
        if crew_name and agent_name:
            primary_name = f"{crew_name}:{agent_name}"
        elif crew_name:
            primary_name = crew_name
        elif agent_name:
            primary_name = agent_name
        else:
            primary_name = "unknown_crew"
        
        # Initialize base tracker
        super().__init__(
            agent_name=primary_name,
            framework_name="crewai",
            session_id=session_id,
            config=config,
            run_env=run_env
        )
        
        # CrewAI-specific tracking state
        self._active_agents: Dict[str, Dict] = {}
        self._crew_execution_id: Optional[str] = None
    
    def extract_model_info(self, *args, **kwargs) -> str:
        """Extract model information from CrewAI function arguments."""
        return self._extract_model_info(args, kwargs)
    
    def _extract_model_info(self, args, kwargs) -> str:
        """Internal method to extract model information from CrewAI function arguments."""
        if 'model' in kwargs:
            return str(kwargs['model'])
        
        if 'llm' in kwargs and hasattr(kwargs['llm'], 'model_name'):
            return kwargs['llm'].model_name
        
        for arg in args:
            if hasattr(arg, 'llm') and hasattr(arg.llm, 'model_name'):
                return arg.llm.model_name
            if hasattr(arg, 'model'):
                return str(arg.model)
            if hasattr(arg, 'agents'):
                for agent in arg.agents:
                    if hasattr(agent, 'llm') and hasattr(agent.llm, 'model_name'):
                        return agent.llm.model_name
        
        return "unknown"
    
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
    
    def simple_track(self, func_name: str = "execution"):
        """Simple decorator for tracking any function with minimal setup."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                execution_id = str(uuid.uuid4())
                
                self.start_operation(execution_id)
                model = self.extract_model_info(*args, **kwargs)
                self.emit_lifecycle_event("start", 0, model, True, agent_name_suffix=func_name)
                
                try:
                    result = func(*args, **kwargs)
                    duration_ms = self.end_operation(execution_id)
                    tool_calls, memory_events = self.get_operation_data(execution_id)
                    
                    self.emit_lifecycle_event("end", duration_ms, model, True,
                                            agent_name_suffix=func_name,
                                            tool_calls=tool_calls, memory_events=memory_events)
                    return result
                    
                except Exception as e:
                    duration_ms = self.end_operation(execution_id)
                    tool_calls, memory_events = self.get_operation_data(execution_id)
                    
                    self.emit_lifecycle_event("error", duration_ms, model, False,
                                            agent_name_suffix=func_name,
                                            exception=type(e).__name__,
                                            tool_calls=tool_calls, memory_events=memory_events)
                    raise
                finally:
                    self.cleanup_operation(execution_id)
            
            return wrapper
        return decorator
    
    def track_task_execution(self, task_name: str, model: str = "unknown"):
        """Context manager for tracking task execution."""
        return TaskExecutionContext(self, task_name, model)
    
    @classmethod
    def auto_track_crew(cls, crew_obj, **tracker_kwargs):
        """
        Enhanced CrewAI tracking that properly captures individual agent execution.
        This version hooks into CrewAI's internal execution flow for better tracking.
        """
        from ..logging_util import logger
        
        # Get crew name
        crew_name = getattr(crew_obj, 'name', None) or "CrewAI_Crew"
        logger.info(f"🤖 Teraace CrewAI: Setting up enhanced tracking for crew '{crew_name}'")
        
        # Create a main crew tracker
        main_tracker = cls(crew_name=crew_name, **tracker_kwargs)
        
        # Track individual agents by wrapping their execution methods
        if hasattr(crew_obj, 'agents') and crew_obj.agents:
            logger.info(f"🎭 Teraace CrewAI: Found {len(crew_obj.agents)} agents to track")
            
            for i, agent in enumerate(crew_obj.agents):
                agent_role = getattr(agent, 'role', f"Agent_{i}")
                logger.info(f"   📝 Setting up tracking for agent: {agent_role}")
                
                # Create individual tracker for this agent
                agent_tracker = cls(
                    crew_name=crew_name,
                    agent_name=agent_role,
                    **tracker_kwargs
                )
                
                # Store the tracker on the agent for reference
                agent._teraace_tracker = agent_tracker
                
                # Wrap the agent's execute method (this is where the real work happens)
                if hasattr(agent, 'execute'):
                    original_execute = agent.execute
                    
                    def make_tracked_execute(tracker, role):
                        def tracked_execute(*args, **kwargs):
                            # Extract task info if available
                            task_info = "unknown_task"
                            if args and hasattr(args[0], 'description'):
                                task_info = args[0].description[:50]
                            
                            logger.info(f"🎯 Teraace CrewAI: Agent '{role}' starting task: {task_info}")
                            
                            # Track the execution
                            execution_id = str(uuid.uuid4())
                            tracker.start_operation(execution_id)
                            
                            # Extract model info
                            model = tracker.extract_model_info(*args, **kwargs)
                            tracker.emit_lifecycle_event("start", 0, model, True)
                            
                            try:
                                result = original_execute(*args, **kwargs)
                                duration_ms = tracker.end_operation(execution_id)
                                tool_calls, memory_events = tracker.get_operation_data(execution_id)
                                
                                tracker.emit_lifecycle_event("end", duration_ms, model, True,
                                                            tool_calls=tool_calls, memory_events=memory_events)
                                
                                logger.info(f"✅ Teraace CrewAI: Agent '{role}' completed task successfully")
                                return result
                                
                            except Exception as e:
                                duration_ms = tracker.end_operation(execution_id)
                                tool_calls, memory_events = tracker.get_operation_data(execution_id)
                                
                                tracker.emit_lifecycle_event("error", duration_ms, model, False,
                                                            exception=type(e).__name__,
                                                            tool_calls=tool_calls, memory_events=memory_events)
                                
                                logger.error(f"❌ Teraace CrewAI: Agent '{role}' task failed: {e}")
                                raise
                            finally:
                                tracker.cleanup_operation(execution_id)
                        
                        return tracked_execute
                    
                    agent.execute = make_tracked_execute(agent_tracker, agent_role)
                
                # Also try to wrap other potential execution methods
                for method_name in ['_execute_task', 'run', 'perform_task']:
                    if hasattr(agent, method_name):
                        original_method = getattr(agent, method_name)
                        
                        def make_tracked_method(tracker, role, method_name):
                            @agent_tracker.simple_track(f"{method_name}")
                            def tracked_method(*args, **kwargs):
                                logger.info(f"🔧 Teraace CrewAI: Agent '{role}' executing {method_name}")
                                return original_method(*args, **kwargs)
                            return tracked_method
                        
                        setattr(agent, method_name, make_tracked_method(agent_tracker, agent_role, method_name))
        
        # Track overall crew execution
        original_kickoff = crew_obj.kickoff
        
        @main_tracker.simple_track("crew_kickoff")
        def tracked_kickoff(*args, **kwargs):
            logger.info(f"🚀 Teraace CrewAI: Starting crew '{crew_name}' execution")
            result = original_kickoff(*args, **kwargs)
            logger.info(f"✅ Teraace CrewAI: Completed crew '{crew_name}' execution")
            return result
        
        crew_obj.kickoff = tracked_kickoff
        crew_obj._teraace_tracker = main_tracker
        
        logger.info(f"✅ Teraace CrewAI: Enhanced tracking setup complete for crew '{crew_name}'")
        return crew_obj
    
    @classmethod
    def auto_track_crew_simple(cls, crew_obj, **tracker_kwargs):
        """
        Simple crew tracking (original method) - tracks only overall execution.
        Use this if the detailed tracking causes issues.
        """
        crew_name = getattr(crew_obj, 'name', None) or "CrewAI_Crew"
        tracker = cls(crew_name=crew_name, **tracker_kwargs)
        
        # Log that auto-tracking is enabled
        from ..logging_util import logger
        logger.info(f"🤖 Teraace CrewAI: Simple auto-tracking enabled for crew '{crew_name}'")
        
        original_kickoff = crew_obj.kickoff
        
        @tracker.simple_track("crew_execution")
        def tracked_kickoff(*args, **kwargs):
            logger.info(f"🚀 Teraace CrewAI: Starting tracked execution for crew '{crew_name}'")
            result = original_kickoff(*args, **kwargs)
            logger.info(f"✅ Teraace CrewAI: Completed tracked execution for crew '{crew_name}'")
            return result
        
        crew_obj.kickoff = tracked_kickoff
        crew_obj._teraace_tracker = tracker
        
        return crew_obj

class TaskExecutionContext:
    """Context manager for tracking CrewAI task execution."""
    
    def __init__(self, tracker: CrewAITracker, task_name: str, model: str):
        self.tracker = tracker
        self.task_name = task_name
        self.model = model
        self.execution_id = str(uuid.uuid4())
        self.start_time = None
    
    def __enter__(self):
        """Enter the context manager - start tracking."""
        self.start_time = time.time()
        self.tracker.start_operation(self.execution_id)
        self.tracker.emit_lifecycle_event("start", 0, self.model, True, agent_name_suffix=self.task_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager - end tracking."""
        try:
            duration_ms = self.tracker.end_operation(self.execution_id)
            tool_calls, memory_events = self.tracker.get_operation_data(self.execution_id)
            
            if exc_type is None:
                self.tracker.emit_lifecycle_event("end", duration_ms, self.model, True,
                                                agent_name_suffix=self.task_name,
                                                tool_calls=tool_calls, memory_events=memory_events)
            else:
                self.tracker.emit_lifecycle_event("error", duration_ms, self.model, False,
                                                agent_name_suffix=self.task_name,
                                                exception=exc_type.__name__ if exc_type else "",
                                                tool_calls=tool_calls, memory_events=memory_events)
        finally:
            self.tracker.cleanup_operation(self.execution_id)
    
    def log_tool_call(self, tool_name: str):
        """Log a tool call within this task context."""
        self.tracker.log_tool_call(tool_name, self.execution_id)
    
    def log_memory_event(self, event_type: str, key: str):
        """Log a memory event within this task context."""
        self.tracker.log_memory_event(event_type, key, self.execution_id)