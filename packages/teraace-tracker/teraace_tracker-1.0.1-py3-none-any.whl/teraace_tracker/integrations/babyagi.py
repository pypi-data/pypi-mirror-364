"""BabyAGI integration for Teraace Agentic Tracker.

BabyAGI is a simple autonomous agent that uses OpenAI and vector databases
to create, prioritize, and execute tasks based on a given objective.
"""

from typing import Any, Dict, List, Optional, Union
from .base import BaseTracker


class BabyAGITracker(BaseTracker):
    """Tracker for BabyAGI autonomous task execution."""
    
    def __init__(self, agent_name: str = "babyagi_agent", **kwargs):
        """Initialize BabyAGI tracker."""
        super().__init__(agent_name=agent_name, framework_name="babyagi", **kwargs)
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
        
        self._emit_event(
            event_type='session_start',
            data=session_data,
            metadata={'framework': self.framework_name}
        )
    
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
        
        self._emit_event(
            event_type='task_creation',
            data=task_data,
            metadata={'framework': self.framework_name}
        )
    
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
        
        self._emit_event(
            event_type='task_prioritization',
            data=prioritization_data,
            metadata={'framework': self.framework_name}
        )
    
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
        
        self._emit_event(
            event_type='task_execution',
            data=execution_data,
            metadata={'framework': self.framework_name}
        )
        
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
        
        self._emit_event(
            event_type='vector_store_operation',
            data=vector_data,
            metadata={'framework': self.framework_name}
        )
    
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
        
        self._emit_event(
            event_type='context_retrieval',
            data=context_data,
            metadata={'framework': self.framework_name}
        )
    
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
        
        self._emit_event(
            event_type='new_task_generation',
            data=generation_data,
            metadata={'framework': self.framework_name}
        )
    
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
        
        self._emit_event(
            event_type='iteration_completion',
            data=iteration_data,
            metadata={'framework': self.framework_name}
        )
    
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
        
        self._emit_event(
            event_type='session_completion',
            data=completion_data,
            metadata={'framework': self.framework_name}
        )
        
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
    
    def _emit_event(self, event_type: str, data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Emit a tracking event."""
        # This is a placeholder - in a real implementation, this would emit to the tracking system
        pass