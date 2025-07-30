"""TaskWeaver integration for Teraace Agentic Tracker.

TaskWeaver is a code-first agent framework that converts tasks into executable 
LLM-generated code with plugin calls. It focuses on task-to-code translation 
and plugin execution rather than multi-agent orchestration.

Note: TaskWeaver does not involve multiple interacting agents or handoffs between 
agents, so multi-agent naming support is not relevant for this framework.
"""

import time
import uuid
from typing import Any, Dict, List, Optional, Union
from functools import wraps

from .base import BaseTracker


class TaskWeaverTracker(BaseTracker):
    """Tracker for TaskWeaver code-first task execution (single-task focused)."""
    
    def __init__(
        self,
        task_name: Optional[str] = None,
        session_id: Optional[str] = None,
        config=None,
        run_env: str = "local",
        **metadata
    ):
        """Initialize TaskWeaver tracker for task-focused operations.
        
        Note: TaskWeaver is not multi-agent, so we focus on task identifiers
        rather than agent names.
        """
        # TaskWeaver is task-focused, not multi-agent
        primary_name = task_name or "taskweaver_task"
        
        # Initialize base tracker
        super().__init__(
            agent_name=primary_name,
            framework_name="taskweaver",
            session_id=session_id,
            config=config,
            run_env=run_env
        )
        
        # TaskWeaver-specific tracking state
        self.task_name = task_name
        self.metadata = metadata
        self._tracked_sessions = {}
        self._tracked_tasks = {}
        self._code_executions = {}
    
    def track_session_creation(self, session: Any, session_config: Dict[str, Any]) -> None:
        """Track TaskWeaver session creation.
        
        Args:
            session: The TaskWeaver session instance
            session_config: Configuration used to create the session
        """
        session_data = {
            'session_id': getattr(session, 'session_id', 'unknown'),
            'session_type': session.__class__.__name__,
            'max_rounds': session_config.get('max_rounds', 10),
            'code_execution_enabled': session_config.get('code_execution_enabled', True),
            'plugins_enabled': len(session_config.get('plugins', [])),
            'llm_config': session_config.get('llm_config', {}),
            'task_name': self.task_name
        }
        
        # Log session creation as a tool call
        self.log_tool_call(f"create_session_{session_data['session_id']}")
        
        # Store session for tracking
        session_id = id(session)
        self._tracked_sessions[session_id] = session
    
    def track_conversation_round(self, session: Any, user_query: str, round_number: int) -> None:
        """Track a conversation round in TaskWeaver.
        
        Args:
            session: The TaskWeaver session
            user_query: The user's query for this round
            round_number: The current round number
        """
        round_data = {
            'session_id': getattr(session, 'session_id', 'unknown'),
            'round_number': round_number,
            'user_query': user_query,
            'query_length': len(user_query),
            'timestamp': getattr(session, 'current_timestamp', None),
            'task_name': self.task_name
        }
        
        # Log conversation round as a tool call
        self.log_tool_call(f"conversation_round_{round_number}_{round_data['session_id']}")
    
    def track_code_generation(self, agent: Any, task: str, generated_code: str, language: str = "python") -> None:
        """Track code generation by TaskWeaver agents.
        
        Args:
            agent: The agent generating code
            task: The task description
            generated_code: The generated code
            language: Programming language (default: python)
        """
        code_data = {
            'agent_type': agent.__class__.__name__,
            'task': task,
            'language': language,
            'code_length': len(generated_code),
            'has_imports': 'import' in generated_code,
            'has_functions': 'def ' in generated_code,
            'has_classes': 'class ' in generated_code,
            'line_count': len(generated_code.split('\n')),
            'task_name': self.task_name
        }
        
        # Log code generation as a tool call
        self.log_tool_call(f"generate_code_{language}_{task[:20]}")
    
    def track_code_execution(self, executor: Any, code: str, execution_result: Dict[str, Any]) -> None:
        """Track code execution in TaskWeaver.
        
        Args:
            executor: The code executor instance
            code: The code being executed
            execution_result: Result of code execution
        """
        execution_data = {
            'executor_type': executor.__class__.__name__,
            'code_length': len(code),
            'execution_status': execution_result.get('status', 'unknown'),
            'has_output': bool(execution_result.get('output')),
            'has_error': bool(execution_result.get('error')),
            'execution_time': execution_result.get('execution_time'),
            'memory_usage': execution_result.get('memory_usage'),
            'task_name': self.task_name
        }
        
        # Log code execution as a tool call
        self.log_tool_call(f"execute_code_{execution_data['executor_type']}")
    
    def track_plugin_execution(self, plugin: Any, function_name: str, arguments: Dict[str, Any], result: Any = None) -> None:
        """Track plugin execution in TaskWeaver.
        
        Args:
            plugin: The plugin being executed
            function_name: Name of the plugin function
            arguments: Arguments passed to the plugin
            result: Result from plugin execution
        """
        plugin_data = {
            'plugin_name': getattr(plugin, 'name', plugin.__class__.__name__),
            'plugin_type': plugin.__class__.__name__,
            'function_name': function_name,
            'argument_count': len(arguments),
            'has_result': result is not None,
            'result_type': type(result).__name__ if result is not None else None,
            'task_name': self.task_name
        }
        
        # Log plugin execution as a tool call
        self.log_tool_call(f"{plugin_data['plugin_name']}_{function_name}")
    
    def track_planner_operation(self, planner: Any, task: str, plan: List[Dict[str, Any]]) -> None:
        """Track planning operations in TaskWeaver.
        
        Args:
            planner: The planner instance
            task: The task to be planned
            plan: The generated plan steps
        """
        plan_data = {
            'planner_type': planner.__class__.__name__,
            'task': task,
            'plan_steps': len(plan),
            'step_types': [step.get('type', 'unknown') for step in plan],
            'estimated_complexity': sum(step.get('complexity', 1) for step in plan),
            'task_name': self.task_name
        }
        
        # Log planner operation as a tool call
        self.log_tool_call(f"plan_task_{plan_data['planner_type']}")
    
    def track_memory_operation(self, memory: Any, operation: str, data: Dict[str, Any]) -> None:
        """Track memory operations in TaskWeaver.
        
        Args:
            memory: The memory instance
            operation: Type of memory operation
            data: Data related to the operation
        """
        memory_data = {
            'memory_type': memory.__class__.__name__,
            'operation': operation,
            'data_keys': list(data.keys()) if isinstance(data, dict) else [],
            'data_size': len(str(data)),
            'task_name': self.task_name
        }
        
        # Log memory operation as a memory event
        self.log_memory_event("memory_operation", f"{memory_data['operation']}_{memory_data['memory_type']}")
    
    def track_conversation_completion(self, session: Any, total_rounds: int, final_result: Any) -> None:
        """Track completion of a TaskWeaver conversation.
        
        Args:
            session: The TaskWeaver session
            total_rounds: Total number of conversation rounds
            final_result: The final result of the conversation
        """
        completion_data = {
            'session_id': getattr(session, 'session_id', 'unknown'),
            'total_rounds': total_rounds,
            'has_final_result': final_result is not None,
            'result_type': type(final_result).__name__ if final_result is not None else None,
            'session_duration': getattr(session, 'duration', None),
            'task_name': self.task_name
        }
        
        # Log conversation completion as a tool call
        self.log_tool_call(f"complete_conversation_{completion_data['session_id']}")
    
    def auto_track_session(self, session: Any, config: Dict[str, Any] = None) -> Any:
        """Automatically track a TaskWeaver session.
        
        Args:
            session: The TaskWeaver session instance
            config: Optional session configuration
            
        Returns:
            The same session (for chaining)
        """
        session_id = id(session)
        self._tracked_sessions[session_id] = session
        
        # Track session creation
        if config:
            self.track_session_creation(session, config)
        
        return session
    
    def extract_model_info(self, *args, **kwargs) -> str:
        """Extract model information from TaskWeaver session."""
        if args and hasattr(args[0], 'llm_config'):
            return args[0].llm_config.get('model', 'gpt-4')
        return kwargs.get('model', 'gpt-4')
    
    def track_task_execution(self, func):
        """Decorator for tracking task execution."""
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
    
    def track_task_context(self, task_name: str, model: str = "unknown"):
        """Context manager for tracking task execution."""
        return TaskExecutionContext(self, task_name, model)


class TaskExecutionContext:
    """Context manager for tracking TaskWeaver task execution."""
    
    def __init__(self, tracker: TaskWeaverTracker, task_name: str, model: str):
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