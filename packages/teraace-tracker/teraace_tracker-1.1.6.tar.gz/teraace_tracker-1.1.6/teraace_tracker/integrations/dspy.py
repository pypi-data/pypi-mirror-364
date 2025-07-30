"""DSPy integration for Teraace Agentic Tracker.

DSPy is a framework for algorithmically optimizing LM prompts and weights,
especially when LMs are used one or more times within a pipeline.
"""

import time
import uuid
from typing import Any, Dict, List, Optional, Union
from functools import wraps

from .base import BaseTracker


class DSPyTracker(BaseTracker):
    """Tracker for DSPy prompt optimization and pipeline execution with workflow support."""
    
    def __init__(
        self,
        workflow_name: Optional[str] = None,
        agent_role: Optional[str] = None,
        session_id: Optional[str] = None,
        config=None,
        run_env: str = "local",
        **metadata
    ):
        """Initialize DSPy tracker with flexible workflow/role support."""
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
            primary_name = "dspy_workflow"
        
        # Initialize base tracker
        super().__init__(
            agent_name=primary_name,
            framework_name="dspy",
            session_id=session_id,
            config=config,
            run_env=run_env
        )
        
        # DSPy-specific tracking state
        self._tracked_modules = {}
        self._optimization_history = []
    
    def track_module_creation(self, module: Any, module_config: Dict[str, Any]) -> None:
        """Track DSPy module creation.
        
        Args:
            module: The DSPy module instance
            module_config: Configuration for the module
        """
        module_data = {
            'module_name': getattr(module, '__class__.__name__', 'unknown'),
            'module_type': module.__class__.__name__,
            'signature': getattr(module, 'signature', None),
            'predictor_type': module_config.get('predictor_type', 'unknown'),
            'lm_model': module_config.get('lm_model', 'unknown'),
            'max_tokens': module_config.get('max_tokens'),
            'temperature': module_config.get('temperature')
        }
        
        # Log module creation as a tool call
        self.log_tool_call(f"create_module_{module_data['module_type']}")
        
        # Store module for tracking
        module_id = id(module)
        self._tracked_modules[module_id] = module
    
    def track_prediction(self, module: Any, input_data: Dict[str, Any], prediction: Any, confidence: float = None) -> None:
        """Track prediction made by DSPy module.
        
        Args:
            module: The DSPy module making the prediction
            input_data: Input data for the prediction
            prediction: The prediction result
            confidence: Optional confidence score
        """
        prediction_data = {
            'module_name': module.__class__.__name__,
            'input_keys': list(input_data.keys()) if isinstance(input_data, dict) else [],
            'prediction_type': type(prediction).__name__,
            'has_confidence': confidence is not None,
            'confidence_score': confidence,
            'prediction_length': len(str(prediction)) if prediction else 0
        }
        
        # Log prediction as a tool call
        self.log_tool_call(f"predict_{prediction_data['module_name']}")
    
    def track_optimization_start(self, optimizer: Any, trainset: List[Any], optimizer_config: Dict[str, Any]) -> None:
        """Track start of DSPy optimization process.
        
        Args:
            optimizer: The optimizer instance
            trainset: Training dataset
            optimizer_config: Optimizer configuration
        """
        optimization_data = {
            'optimizer_type': optimizer.__class__.__name__,
            'trainset_size': len(trainset),
            'max_bootstrapped_demos': optimizer_config.get('max_bootstrapped_demos', 4),
            'max_labeled_demos': optimizer_config.get('max_labeled_demos', 16),
            'num_candidate_programs': optimizer_config.get('num_candidate_programs', 16),
            'num_threads': optimizer_config.get('num_threads', 6)
        }
        
        # Log optimization start as a memory event
        self.log_memory_event("optimization_start", f"{optimization_data['optimizer_type']}_trainset_{optimization_data['trainset_size']}")
    
    def track_optimization_step(self, optimizer: Any, step_number: int, step_result: Dict[str, Any]) -> None:
        """Track individual optimization step.
        
        Args:
            optimizer: The optimizer instance
            step_number: Current optimization step
            step_result: Results from this step
        """
        step_data = {
            'optimizer_type': optimizer.__class__.__name__,
            'step_number': step_number,
            'score': step_result.get('score', 0.0),
            'num_examples': step_result.get('num_examples', 0),
            'improvement': step_result.get('improvement', 0.0),
            'best_score_so_far': step_result.get('best_score_so_far', 0.0)
        }
        
        # Log optimization step as a memory event
        self.log_memory_event("optimization_step", f"step_{step_number}_score_{step_data['score']}")
        
        # Store in optimization history
        self._optimization_history.append(step_data)
    
    def track_prompt_generation(self, module: Any, generated_prompt: str, examples: List[Any] = None) -> None:
        """Track prompt generation and optimization.
        
        Args:
            module: The module generating the prompt
            generated_prompt: The generated prompt text
            examples: Optional examples used in prompt
        """
        prompt_data = {
            'module_name': module.__class__.__name__,
            'prompt_length': len(generated_prompt),
            'num_examples': len(examples) if examples else 0,
            'has_examples': examples is not None and len(examples) > 0,
            'prompt_complexity': generated_prompt.count('\n') + 1  # Simple complexity metric
        }
        
        # Log prompt generation as a tool call
        self.log_tool_call(f"generate_prompt_{prompt_data['module_name']}")
    
    def track_pipeline_execution(self, pipeline: Any, input_data: Dict[str, Any], output_data: Dict[str, Any]) -> None:
        """Track execution of DSPy pipeline.
        
        Args:
            pipeline: The DSPy pipeline
            input_data: Input to the pipeline
            output_data: Output from the pipeline
        """
        pipeline_data = {
            'pipeline_type': pipeline.__class__.__name__,
            'input_keys': list(input_data.keys()) if isinstance(input_data, dict) else [],
            'output_keys': list(output_data.keys()) if isinstance(output_data, dict) else [],
            'num_modules': len(getattr(pipeline, 'modules', [])),
            'execution_successful': output_data is not None
        }
        
        # Log pipeline execution as a tool call
        self.log_tool_call(f"execute_pipeline_{pipeline_data['pipeline_type']}")
    
    def track_evaluation(self, evaluator: Any, dataset: List[Any], results: Dict[str, Any]) -> None:
        """Track evaluation of DSPy modules.
        
        Args:
            evaluator: The evaluation function/class
            dataset: Dataset used for evaluation
            results: Evaluation results
        """
        evaluation_data = {
            'evaluator_type': evaluator.__class__.__name__ if hasattr(evaluator, '__class__') else 'function',
            'dataset_size': len(dataset),
            'accuracy': results.get('accuracy', 0.0),
            'precision': results.get('precision', 0.0),
            'recall': results.get('recall', 0.0),
            'f1_score': results.get('f1_score', 0.0),
            'custom_metrics': {k: v for k, v in results.items() if k not in ['accuracy', 'precision', 'recall', 'f1_score']}
        }
        
        # Log evaluation as a tool call
        self.log_tool_call(f"evaluate_{evaluation_data['evaluator_type']}_dataset_{evaluation_data['dataset_size']}")
    
    def track_optimization_completion(self, optimizer: Any, final_results: Dict[str, Any]) -> None:
        """Track completion of optimization process.
        
        Args:
            optimizer: The optimizer instance
            final_results: Final optimization results
        """
        completion_data = {
            'optimizer_type': optimizer.__class__.__name__,
            'total_steps': len(self._optimization_history),
            'final_score': final_results.get('final_score', 0.0),
            'best_score': final_results.get('best_score', 0.0),
            'improvement': final_results.get('improvement', 0.0),
            'optimization_time': final_results.get('optimization_time'),
            'converged': final_results.get('converged', False)
        }
        
        # Log optimization completion as a memory event
        self.log_memory_event("optimization_completion", f"{completion_data['optimizer_type']}_final_score_{completion_data['final_score']}")
        
        # Clear optimization history
        self._optimization_history.clear()
    
    def auto_track_module(self, module: Any, config: Dict[str, Any] = None) -> Any:
        """Automatically track a DSPy module.
        
        Args:
            module: The DSPy module instance
            config: Optional module configuration
            
        Returns:
            The same module (for chaining)
        """
        module_id = id(module)
        self._tracked_modules[module_id] = module
        
        # Track module creation if config is provided
        if config:
            self.track_module_creation(module, config)
        
        return module
    
    def extract_model_info(self, *args, **kwargs) -> str:
        """Extract model information from DSPy module."""
        return kwargs.get('lm_model', 'gpt-3.5-turbo')
    
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
    
    def track_workflow_execution(self, workflow_name: str, model: str = "unknown"):
        """Context manager for tracking workflow execution."""
        return WorkflowExecutionContext(self, workflow_name, model)
    
    @classmethod
    def auto_track_workflow_with_roles(cls, workflow_name: str, agent_roles: List[str], **tracker_kwargs):
        """
        Automatically set up tracking for a DSPy workflow with multiple roles.
        This is the easiest way to get started - just specify the workflow and roles.
        """
        trackers = {}
        for role in agent_roles:
            tracker = cls(workflow_name=workflow_name, agent_role=role, **tracker_kwargs)
            trackers[role] = tracker
        
        return trackers if len(agent_roles) > 1 else trackers[agent_roles[0]]

class WorkflowExecutionContext:
    """Context manager for tracking DSPy workflow execution."""
    
    def __init__(self, tracker: DSPyTracker, workflow_name: str, model: str):
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