"""
Haystack integration for Teraace tracker.
"""

import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Callable
from functools import wraps

from .base import BaseTracker, register_integration
from ..emitter import EventEmitter
from ..config import Config
from ..logging_util import logger


@register_integration("haystack")
class HaystackTracker(BaseTracker):
    """Haystack integration for tracking agent and pipeline events."""
    
    def __init__(
        self,
        agent_name: str,
        session_id: Optional[str] = None,
        config: Optional[Config] = None,
        run_env: str = "local"
    ):
        """
        Initialize Haystack tracker.
        
        Args:
            agent_name: Name of the agent being tracked
            session_id: Session identifier (auto-generated if not provided)
            config: Teraace configuration
            run_env: Runtime environment ('local', 'cloud', etc.)
        """
        super().__init__(agent_name, "haystack", session_id, config, run_env)
        
        logger.info(f"Haystack tracker initialized for agent '{agent_name}' session '{self.session_id}'")
    
    def extract_model_info(self, *args, **kwargs) -> str:
        """
        Extract model information from Haystack objects.
        
        Args:
            *args: Positional arguments that might contain model info
            **kwargs: Keyword arguments that might contain model info
            
        Returns:
            Model name or 'unknown'
        """
        # Try to extract from common Haystack patterns
        model_fields = ['model_name', 'model', 'model_name_or_path', 'generator_model']
        
        # Check kwargs first
        for field in model_fields:
            if field in kwargs and kwargs[field]:
                return str(kwargs[field])
        
        # Check positional arguments for Haystack components
        for arg in args:
            # Check for generator/reader components
            if hasattr(arg, 'model_name_or_path'):
                return str(arg.model_name_or_path)
            if hasattr(arg, 'model_name'):
                return str(arg.model_name)
            if hasattr(arg, 'model'):
                return str(arg.model)
            
            # Check for pipeline components
            if hasattr(arg, 'generator') and hasattr(arg.generator, 'model_name_or_path'):
                return str(arg.generator.model_name_or_path)
            if hasattr(arg, 'reader') and hasattr(arg.reader, 'model_name_or_path'):
                return str(arg.reader.model_name_or_path)
        
        return "unknown"
    
    def create_pipeline_execution_decorator(self, func):
        """
        Decorator to track Haystack pipeline execution.
        
        Args:
            func: Function to wrap and track
            
        Returns:
            Wrapped function with event tracking
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            operation_id = str(uuid.uuid4())
            self.start_operation(operation_id)
            
            model = self.extract_model_info(*args, **kwargs)
            
            # Emit start event
            self.emit_lifecycle_event(
                event_type="start",
                duration_ms=0,
                model=model,
                success=True
            )
            
            try:
                result = func(*args, **kwargs)
                
                duration_ms = self.end_operation(operation_id)
                tool_calls, memory_events = self.get_operation_data(operation_id)
                
                # Emit success event
                self.emit_lifecycle_event(
                    event_type="end",
                    duration_ms=duration_ms,
                    model=model,
                    success=True,
                    tool_calls=tool_calls,
                    memory_events=memory_events
                )
                
                return result
                
            except Exception as e:
                duration_ms = self.end_operation(operation_id)
                tool_calls, memory_events = self.get_operation_data(operation_id)
                
                # Emit error event
                self.emit_lifecycle_event(
                    event_type="error",
                    duration_ms=duration_ms,
                    model=model,
                    success=False,
                    exception=type(e).__name__,
                    tool_calls=tool_calls,
                    memory_events=memory_events
                )
                
                raise
            
            finally:
                self.cleanup_operation(operation_id)
        
        return wrapper
    
    def track_node_execution(self, node_name: str, model: str = "unknown"):
        """
        Context manager for tracking Haystack node execution.
        
        Args:
            node_name: Name of the node being executed
            model: Model being used for the node
            
        Returns:
            Context manager for node tracking
        """
        return NodeExecutionContext(self, node_name, model)
    
    def track_agent_execution(self, agent_type: str, model: str = "unknown"):
        """
        Context manager for tracking Haystack agent execution.
        
        Args:
            agent_type: Type of agent being executed
            model: Model being used for the agent
            
        Returns:
            Context manager for agent tracking
        """
        return AgentExecutionContext(self, agent_type, model)
    
    def log_node_call(self, node_name: str, operation_id: Optional[str] = None):
        """
        Log a node execution event.
        
        Args:
            node_name: Name of the node being called
            operation_id: Operation ID to associate with (optional)
        """
        self.log_tool_call(f"node:{node_name}", operation_id)
    
    def log_retriever_call(self, retriever_name: str, operation_id: Optional[str] = None):
        """
        Log a retriever call event.
        
        Args:
            retriever_name: Name of the retriever being called
            operation_id: Operation ID to associate with (optional)
        """
        self.log_tool_call(f"retriever:{retriever_name}", operation_id)
    
    def log_generator_call(self, generator_name: str, operation_id: Optional[str] = None):
        """
        Log a generator call event.
        
        Args:
            generator_name: Name of the generator being called
            operation_id: Operation ID to associate with (optional)
        """
        self.log_tool_call(f"generator:{generator_name}", operation_id)
    
    def log_document_store_access(self, event_type: str, store_name: str, operation_id: Optional[str] = None):
        """
        Log a document store access event.
        
        Args:
            event_type: Type of access ('read', 'write', 'update')
            store_name: Name of the document store
            operation_id: Operation ID to associate with (optional)
        """
        self.log_memory_event(event_type, f"document_store:{store_name}", operation_id)
    
    def _emit_event(self, event_type: str, data: Dict[str, Any], timestamp: Optional[datetime] = None):
        """
        Emit a custom event with the given type and data.
        
        Args:
            event_type: Type of the event
            data: Event data dictionary
            timestamp: Optional timestamp for the event
        """
        # Create a basic agent event with the custom data
        self.emitter.emit_agent_event(
            agent_name=self.agent_name,
            session_id=self.session_id,
            agent_framework=self.framework_name,
            model=data.get('model', 'unknown'),
            event_type=event_type,
            duration_ms=data.get('duration_ms', 0),
            success=data.get('success', True),
            exception=data.get('exception', ''),
            tool_calls=[],
            memory_events=[],
            run_env=self.run_env,
            timestamp=timestamp
        )
    
    def track_pipeline_execution(self, pipeline, query: Dict[str, Any]):
        """
        Track pipeline execution event.
        
        Args:
            pipeline: Haystack pipeline object
            query: Query being processed
        """
        self._emit_event(
            event_type='pipeline_execution_start',
            data={
                'pipeline_type': pipeline.__class__.__name__,
                'model': self.extract_model_info(pipeline)
            }
        )
    
    def track_node_processing(self, node, inputs: Dict[str, Any], outputs: Dict[str, Any]):
        """
        Track node processing event.
        
        Args:
            node: Haystack node object
            inputs: Input data
            outputs: Output data
        """
        self._emit_event(
            event_type='node_processing',
            data={
                'node_type': node.__class__.__name__,
                'model': self.extract_model_info(node)
            }
        )
    
    def track_document_processing(self, processor, documents: List[Dict[str, Any]]):
        """
        Track document processing event.
        
        Args:
            processor: Document processor object
            documents: List of documents being processed
        """
        self._emit_event(
            event_type='document_processing',
            data={
                'processor_type': processor.__class__.__name__,
                'document_count': len(documents),
                'model': self.extract_model_info(processor)
            }
        )
    
    def track_retriever_query(self, retriever, query: str, results: List[Dict[str, Any]]):
        """
        Track retriever query event.
        
        Args:
            retriever: Retriever object
            query: Search query
            results: Retrieved results
        """
        self._emit_event(
            event_type='retriever_query',
            data={
                'retriever_type': retriever.__class__.__name__,
                'query': query,
                'result_count': len(results),
                'model': self.extract_model_info(retriever)
            }
        )
    
    def track_agent_step(self, agent, step_type: str, data: Dict[str, Any]):
        """
        Track agent step event.
        
        Args:
            agent: Agent object
            step_type: Type of step being performed
            data: Step data
        """
        self._emit_event(
            event_type='agent_step',
            data={
                'agent_type': agent.__class__.__name__,
                'step_type': step_type,
                'model': self.extract_model_info(agent)
            }
        )
    
    def auto_track_pipeline(self, pipeline):
        """
        Automatically track a Haystack pipeline.
        
        Args:
            pipeline: Haystack pipeline object to track
            
        Returns:
            The pipeline object (for chaining)
        """
        self._tracked_pipeline = pipeline
        return pipeline


class NodeExecutionContext:
    """Context manager for tracking Haystack node execution."""
    
    def __init__(self, tracker: HaystackTracker, node_name: str, model: str):
        """
        Initialize node execution context.
        
        Args:
            tracker: Haystack tracker instance
            node_name: Name of the node
            model: Model being used
        """
        self.tracker = tracker
        self.node_name = node_name
        self.model = model
        self.operation_id = str(uuid.uuid4())
    
    def __enter__(self):
        """Enter the context manager."""
        self.tracker.start_operation(self.operation_id)
        
        # Emit start event
        self.tracker.emit_lifecycle_event(
            event_type="start",
            duration_ms=0,
            model=self.model,
            success=True,
            agent_name_suffix=f"node:{self.node_name}"
        )
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        duration_ms = self.tracker.end_operation(self.operation_id)
        tool_calls, memory_events = self.tracker.get_operation_data(self.operation_id)
        
        if exc_type is None:
            # Success
            self.tracker.emit_lifecycle_event(
                event_type="end",
                duration_ms=duration_ms,
                model=self.model,
                success=True,
                tool_calls=tool_calls,
                memory_events=memory_events,
                agent_name_suffix=f"node:{self.node_name}"
            )
        else:
            # Error
            self.tracker.emit_lifecycle_event(
                event_type="error",
                duration_ms=duration_ms,
                model=self.model,
                success=False,
                exception=exc_type.__name__ if exc_type else "",
                tool_calls=tool_calls,
                memory_events=memory_events,
                agent_name_suffix=f"node:{self.node_name}"
            )
        
        # Clean up
        self.tracker.cleanup_operation(self.operation_id)
    
    def log_node_call(self, node_name: str):
        """Log a node call within this context."""
        self.tracker.log_node_call(node_name, self.operation_id)
    
    def log_retriever_call(self, retriever_name: str):
        """Log a retriever call within this context."""
        self.tracker.log_retriever_call(retriever_name, self.operation_id)
    
    def log_generator_call(self, generator_name: str):
        """Log a generator call within this context."""
        self.tracker.log_generator_call(generator_name, self.operation_id)
    
    def log_document_store_access(self, event_type: str, store_name: str):
        """Log a document store access within this context."""
        self.tracker.log_document_store_access(event_type, store_name, self.operation_id)


class AgentExecutionContext:
    """Context manager for tracking Haystack agent execution."""
    
    def __init__(self, tracker: HaystackTracker, agent_type: str, model: str):
        """
        Initialize agent execution context.
        
        Args:
            tracker: Haystack tracker instance
            agent_type: Type of agent
            model: Model being used
        """
        self.tracker = tracker
        self.agent_type = agent_type
        self.model = model
        self.operation_id = str(uuid.uuid4())
    
    def __enter__(self):
        """Enter the context manager."""
        self.tracker.start_operation(self.operation_id)
        
        # Emit start event
        self.tracker.emit_lifecycle_event(
            event_type="start",
            duration_ms=0,
            model=self.model,
            success=True,
            agent_name_suffix=f"agent:{self.agent_type}"
        )
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        duration_ms = self.tracker.end_operation(self.operation_id)
        tool_calls, memory_events = self.tracker.get_operation_data(self.operation_id)
        
        if exc_type is None:
            # Success
            self.tracker.emit_lifecycle_event(
                event_type="end",
                duration_ms=duration_ms,
                model=self.model,
                success=True,
                tool_calls=tool_calls,
                memory_events=memory_events,
                agent_name_suffix=f"agent:{self.agent_type}"
            )
        else:
            # Error
            self.tracker.emit_lifecycle_event(
                event_type="error",
                duration_ms=duration_ms,
                model=self.model,
                success=False,
                exception=exc_type.__name__ if exc_type else "",
                tool_calls=tool_calls,
                memory_events=memory_events,
                agent_name_suffix=f"agent:{self.agent_type}"
            )
        
        # Clean up
        self.tracker.cleanup_operation(self.operation_id)
    
    def log_node_call(self, node_name: str):
        """Log a node call within this agent context."""
        self.tracker.log_node_call(node_name, self.operation_id)
    
    def log_document_store_access(self, event_type: str, store_name: str):
        """Log a document store access within this agent context."""
        self.tracker.log_document_store_access(event_type, store_name, self.operation_id)