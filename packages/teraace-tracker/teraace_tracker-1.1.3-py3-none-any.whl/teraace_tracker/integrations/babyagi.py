"""BabyAGI integration for Teraace Agentic Tracker.

BabyAGI is a simple autonomous agent that uses OpenAI and vector databases
to create, prioritize, and execute tasks based on a given objective.
"""

import time
import uuid
from typing import Any, Dict, List, Optional, Union
from functools import wraps

from .base import BaseTracker


class BabyAGITracker(BaseTracker):
    """Tracker for BabyAGI autonomous task execution with workflow support."""
    
    def __init__(
        self,
        workflow_name: Optional[str] = None,
        agent_role: Optional[str] = None,
        session_id: Optional[str] = None,
        config=None,
        run_env: str = "local",
        **metadata
    ):
        """Initialize BabyAGI tracker with flexible workflow/role support."""
        # Store original parameters
        self.workflow_name = workflow_name
        self.agent_role_only = agent_role
        self.metadata = metadata
        
        # Determine the primary identifier for tracking
        if workflow_name and agent_role:
            primary_name = f"{workflow_name}:{agent_role}"
        elif workflow_name:
            primary_name = workflow_name
        elif agent_role:
            primary_name = agent_role
        else:
            primary_name = "babyagi_workflow"
        
        # Initialize base tracker
        super().__init__(
            agent_name=primary_name,
            framework_name="babyagi",
            session_id=session_id,
            config=config,
            run_env=run_env
        )
        
        # BabyAGI-specific tracking state
        self._tracked_sessions = {}
        self._task_history = []
    
    def track_session_start(self, objective: str, initial_task: str, session_config: Dict[str, Any] = None) -> None:
        """Track the start of a BabyAGI session.
        
        Args:
            objective: The main objective for the session
            initial_task: The first task to execute
            session_config: Optional session configuration
        """
        session_data = {
            'objective': objective,
            'initial_task': initial_task,
            'objective_length': len(objective),
            'model': session_config.get('model', 'gpt-3.5-turbo') if session_config else 'gpt-3.5-turbo',
            'max_iterations': session_config.get('max_iterations', 5) if session_config else 5,
            'vector_store': session_config.get('vector_store', 'pinecone') if session_config else 'pinecone'
        }
        
        # Log session start as a memory event
        self.log_memory_event("session_start", f"objective_{len(objective)}_chars")
    
    def track_task_creation(self, task: Dict[str, Any], task_list: List[Dict[str, Any]]) -> None:
        """Track creation of new tasks by BabyAGI.
        
        Args:
            task: The newly created task
            task_list: Current list of all tasks
        """
        task_data = {
            'task_id': task.get('id'),
            'task_name': task.get('task_name', ''),
            'task_description': task.get('description', ''),
            'task_priority': task.get('priority', 0),
            'total_tasks_in_list': len(task_list),
            'task_source': task.get('source', 'generated')
        }
        
        # Log task creation as a tool call
        self.log_tool_call(f"create_task_{task.get('task_name', 'unknown')}")
    
    def track_task_prioritization(self, task_list: List[Dict[str, Any]], prioritized_list: List[Dict[str, Any]]) -> None:
        """Track task prioritization by BabyAGI.
        
        Args:
            task_list: Original task list
            prioritized_list: Prioritized task list
        """
        prioritization_data = {
            'original_task_count': len(task_list),
            'prioritized_task_count': len(prioritized_list),
            'priority_changes': sum(1 for i, task in enumerate(prioritized_list) 
                                  if i < len(task_list) and task.get('id') != task_list[i].get('id')),
            'highest_priority_task': prioritized_list[0].get('task_name', '') if prioritized_list else '',
            'lowest_priority_task': prioritized_list[-1].get('task_name', '') if prioritized_list else ''
        }
        
        # Log task prioritization as a tool call
        self.log_tool_call(f"prioritize_{len(prioritized_list)}_tasks")
    
    def track_task_execution(self, task: Dict[str, Any], execution_result: str, context: List[str] = None) -> None:
        """Track execution of a task by BabyAGI.
        
        Args:
            task: The task being executed
            execution_result: Result of task execution
            context: Optional context from vector store
        """
        execution_data = {
            'task_id': task.get('id'),
            'task_name': task.get('task_name', ''),
            'execution_result': execution_result,
            'result_length': len(execution_result),
            'context_provided': context is not None,
            'context_items': len(context) if context else 0,
            'execution_timestamp': task.get('executed_at')
        }
        
        # Log task execution as a tool call
        self.log_tool_call(f"execute_task_{task.get('task_name', 'unknown')}")
        
        # Store in task history
        self._task_history.append({
            'task': task,
            'result': execution_result,
            'timestamp': task.get('executed_at')
        })
    
    def track_vector_store_operation(self, operation: str, data: Dict[str, Any]) -> None:
        """Track vector store operations in BabyAGI.
        
        Args:
            operation: Type of vector store operation (store, query, update)
            data: Data related to the operation
        """
        vector_data = {
            'operation': operation,
            'vector_store_type': data.get('store_type', 'unknown'),
            'embedding_dimension': data.get('embedding_dimension'),
            'query_text': data.get('query_text', ''),
            'result_count': data.get('result_count', 0),
            'similarity_threshold': data.get('similarity_threshold')
        }
        
        # Log vector store operation as a tool call
        self.log_tool_call(f"vector_{operation}_{data.get('store_type', 'unknown')}")
    
    def track_context_retrieval(self, query: str, retrieved_context: List[str], similarity_scores: List[float] = None) -> None:
        """Track context retrieval from vector store.
        
        Args:
            query: The query used for context retrieval
            retrieved_context: List of retrieved context items
            similarity_scores: Optional similarity scores for retrieved items
        """
        context_data = {
            'query': query,
            'query_length': len(query),
            'context_count': len(retrieved_context),
            'avg_context_length': sum(len(ctx) for ctx in retrieved_context) / len(retrieved_context) if retrieved_context else 0,
            'has_similarity_scores': similarity_scores is not None,
            'avg_similarity': sum(similarity_scores) / len(similarity_scores) if similarity_scores else None
        }
        
        # Log context retrieval as a memory event
        self.log_memory_event("context_retrieval", f"query_{len(query)}_chars")
    
    def track_new_task_generation(self, completed_task: Dict[str, Any], task_result: str, new_tasks: List[Dict[str, Any]]) -> None:
        """Track generation of new tasks based on completed task.
        
        Args:
            completed_task: The task that was just completed
            task_result: Result of the completed task
            new_tasks: List of newly generated tasks
        """
        generation_data = {
            'completed_task_name': completed_task.get('task_name', ''),
            'completed_task_id': completed_task.get('id'),
            'result_length': len(task_result),
            'new_task_count': len(new_tasks),
            'new_task_names': [task.get('task_name', '') for task in new_tasks],
            'generation_successful': len(new_tasks) > 0
        }
        
        # Log new task generation as a tool call
        self.log_tool_call(f"generate_{len(new_tasks)}_new_tasks")
    
    def track_iteration_completion(self, iteration_number: int, completed_task: Dict[str, Any], remaining_tasks: int) -> None:
        """Track completion of a BabyAGI iteration.
        
        Args:
            iteration_number: The iteration number
            completed_task: The task that was completed in this iteration
            remaining_tasks: Number of tasks remaining in the queue
        """
        iteration_data = {
            'iteration_number': iteration_number,
            'completed_task_name': completed_task.get('task_name', ''),
            'completed_task_id': completed_task.get('id'),
            'remaining_tasks': remaining_tasks,
            'total_tasks_completed': len(self._task_history),
            'iteration_timestamp': completed_task.get('executed_at')
        }
        
        # Log iteration completion as a memory event
        self.log_memory_event("iteration_completion", f"iteration_{iteration_number}_remaining_{remaining_tasks}")
    
    def track_session_completion(self, objective: str, total_iterations: int, final_status: str) -> None:
        """Track completion of a BabyAGI session.
        
        Args:
            objective: The original objective
            total_iterations: Total number of iterations completed
            final_status: Final status of the session
        """
        completion_data = {
            'objective': objective,
            'total_iterations': total_iterations,
            'total_tasks_completed': len(self._task_history),
            'final_status': final_status,
            'objective_achieved': final_status == 'completed',
            'session_duration': None  # Could be calculated if timestamps are available
        }
        
        # Log session completion as a memory event
        self.log_memory_event("session_completion", f"status_{final_status}_iterations_{total_iterations}")
        
        # Clear task history for next session
        self._task_history.clear()
    
    def auto_track_session(self, objective: str, initial_task: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Automatically track a BabyAGI session.
        
        Args:
            objective: The main objective
            initial_task: The initial task
            config: Optional configuration
            
        Returns:
            Session tracking data
        """
        session_data = {
            'objective': objective,
            'initial_task': initial_task,
            'config': config or {}
        }
        
        # Track session start
        self.track_session_start(objective, initial_task, config)
        
        return session_data
    
    def extract_model_info(self, *args, **kwargs) -> str:
        """Extract model information from BabyAGI session config."""
        if args and isinstance(args[0], dict):
            return args[0].get('model', 'gpt-3.5-turbo')
        return kwargs.get('model', 'gpt-3.5-turbo')
    
    def track_workflow_execution(self, workflow_name: str, model: str = "unknown"):
        """Context manager for tracking workflow execution."""
        return WorkflowExecutionContext(self, workflow_name, model)
    
    @classmethod
    def auto_track_workflow(cls, workflow_name: str, agent_roles: List[str] = None, **tracker_kwargs):
        """
        Automatically set up tracking for a BabyAGI workflow with multiple roles.
        This is the easiest way to get started - just specify the workflow and roles.
        """
        if not agent_roles:
            agent_roles = ["TaskCreator", "TaskPrioritizer", "TaskExecutor"]
        
        trackers = {}
        for role in agent_roles:
            tracker = cls(workflow_name=workflow_name, agent_role=role, **tracker_kwargs)
            trackers[role] = tracker
        
        return trackers if len(agent_roles) > 1 else trackers[agent_roles[0]]

class WorkflowExecutionContext:
    """Context manager for tracking BabyAGI workflow execution."""
    
    def __init__(self, tracker: BabyAGITracker, workflow_name: str, model: str):
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