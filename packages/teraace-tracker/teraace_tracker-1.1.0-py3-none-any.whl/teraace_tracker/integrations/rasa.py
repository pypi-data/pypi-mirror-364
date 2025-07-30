"""
Rasa integration for Teraace tracker.
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


@register_integration("rasa")
class RasaTracker(BaseTracker):
    """Rasa integration for tracking conversational agent events.
    
    Note: Rasa is a conversational AI framework centered on intent recognition 
    and dialogue flows, not multi-agent orchestration. "Agents" in Rasa refer 
    to NLU models and bots rather than multiple collaborating AI agents.
    """
    
    def __init__(
        self,
        agent_name: str,
        session_id: Optional[str] = None,
        config: Optional[Config] = None,
        run_env: str = "local"
    ):
        """
        Initialize Rasa tracker for single conversational agent.
        
        Args:
            agent_name: Name of the conversational agent being tracked
            session_id: Session identifier (auto-generated if not provided)
            config: Teraace configuration
            run_env: Runtime environment ('local', 'cloud', etc.)
        """
        super().__init__(agent_name, "rasa", session_id, config, run_env)
        
        logger.info(f"Rasa tracker initialized for agent '{agent_name}' session '{self.session_id}'")
    
    def extract_model_info(self, *args, **kwargs) -> str:
        """
        Extract model information from Rasa objects.
        
        Args:
            *args: Positional arguments that might contain model info
            **kwargs: Keyword arguments that might contain model info
            
        Returns:
            Model name or 'unknown'
        """
        # Try to extract from common Rasa patterns
        model_fields = ['model_name', 'model', 'nlu_model', 'core_model', 'pipeline']
        
        # Check kwargs first
        for field in model_fields:
            if field in kwargs and kwargs[field]:
                return str(kwargs[field])
        
        # Check positional arguments for Rasa components
        for arg in args:
            # Check for agent/interpreter objects
            if hasattr(arg, 'model_directory'):
                return f"rasa_model:{arg.model_directory}"
            if hasattr(arg, 'model_metadata') and hasattr(arg.model_metadata, 'get'):
                pipeline = arg.model_metadata.get('pipeline', [])
                if pipeline and len(pipeline) > 0:
                    return f"pipeline:{pipeline[0].get('name', 'unknown')}"
            
            # Check for domain objects
            if hasattr(arg, 'domain') and hasattr(arg.domain, 'as_dict'):
                return "rasa_domain"
            
            # Check for tracker objects
            if hasattr(arg, 'sender_id'):
                return f"conversation:{arg.sender_id}"
        
        return "rasa_default"
    
    def track_message_processing(self, func):
        """
        Decorator to track Rasa message processing.
        
        Args:
            func: Function to wrap and track
            
        Returns:
            Wrapped function with event tracking
        """
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
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
                result = await func(*args, **kwargs)
                
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
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
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
        
        # Return appropriate wrapper based on whether function is async
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    def create_dialogue_turn_context(self, turn_id: str, model: str = "rasa_default"):
        """
        Context manager for tracking Rasa dialogue turn.
        
        Args:
            turn_id: Identifier for the dialogue turn
            model: Model being used for the turn
            
        Returns:
            Context manager for dialogue turn tracking
        """
        return DialogueTurnContext(self, turn_id, model)
    
    def create_action_execution_context(self, action_name: str, model: str = "rasa_default"):
        """
        Context manager for tracking Rasa action execution.
        
        Args:
            action_name: Name of the action being executed
            model: Model being used for the action
            
        Returns:
            Context manager for action tracking
        """
        return ActionExecutionContext(self, action_name, model)
    
    def log_intent_classification(self, intent_name: str, confidence: float, operation_id: Optional[str] = None):
        """
        Log an intent classification event.
        
        Args:
            intent_name: Name of the classified intent
            confidence: Confidence score of the classification
            operation_id: Operation ID to associate with (optional)
        """
        self.log_tool_call(f"intent:{intent_name}:{confidence:.2f}", operation_id)
    
    def log_entity_extraction(self, entity_type: str, entity_value: str, operation_id: Optional[str] = None):
        """
        Log an entity extraction event.
        
        Args:
            entity_type: Type of the extracted entity
            entity_value: Value of the extracted entity
            operation_id: Operation ID to associate with (optional)
        """
        self.log_tool_call(f"entity:{entity_type}:{entity_value}", operation_id)
    
    def log_action_execution(self, action_name: str, operation_id: Optional[str] = None):
        """
        Log an action execution event.
        
        Args:
            action_name: Name of the action being executed
            operation_id: Operation ID to associate with (optional)
        """
        self.log_tool_call(f"action:{action_name}", operation_id)
    
    def log_slot_update(self, slot_name: str, slot_value: str, operation_id: Optional[str] = None):
        """
        Log a slot update event.
        
        Args:
            slot_name: Name of the slot being updated
            slot_value: New value of the slot
            operation_id: Operation ID to associate with (optional)
        """
        self.log_memory_event("update", f"slot:{slot_name}:{slot_value}", operation_id)
    
    def log_story_prediction(self, story_name: str, operation_id: Optional[str] = None):
        """
        Log a story prediction event.
        
        Args:
            story_name: Name of the predicted story
            operation_id: Operation ID to associate with (optional)
        """
        self.log_memory_event("read", f"story:{story_name}", operation_id)
    
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
    
    def track_intent_classification(self, interpreter, text: str, message: Dict[str, Any]):
        """
        Track intent classification event.
        
        Args:
            interpreter: Rasa NLU interpreter
            text: Input text
            message: Parsed message with intent information
        """
        intent_data = message.get('intent', {})
        self._emit_event(
            event_type='intent_classification',
            data={
                'interpreter_type': interpreter.__class__.__name__,
                'text': text,
                'intent': intent_data.get('name', 'unknown'),
                'confidence': intent_data.get('confidence', 0.0),
                'model': self.extract_model_info(interpreter)
            }
        )
    
    def track_action_execution(self, action, tracker, dispatcher):
        """
        Track action execution event.
        
        Args:
            action: Rasa action object
            tracker: Rasa dialogue tracker
            dispatcher: Rasa dispatcher
        """
        action_name = action.name() if hasattr(action, 'name') and callable(action.name) else str(action)
        self._emit_event(
            event_type='action_execution_start',
            data={
                'action_name': action_name,
                'action_type': action.__class__.__name__,
                'model': self.extract_model_info(action, tracker, dispatcher)
            }
        )
    
    def track_dialogue_turn(self, tracker, turn_type: str):
        """
        Track dialogue turn event.
        
        Args:
            tracker: Rasa dialogue tracker
            turn_type: Type of turn (e.g., 'user_message', 'bot_response')
        """
        latest_message = getattr(tracker, 'latest_message', {})
        self._emit_event(
            event_type='dialogue_turn',
            data={
                'sender_id': getattr(tracker, 'sender_id', 'unknown'),
                'turn_type': turn_type,
                'message': latest_message,
                'model': self.extract_model_info(tracker)
            }
        )
    
    def track_policy_prediction(self, policy, tracker, domain, prediction: Dict[str, Any]):
        """
        Track policy prediction event.
        
        Args:
            policy: Rasa policy object
            tracker: Rasa dialogue tracker
            domain: Rasa domain
            prediction: Policy prediction result
        """
        self._emit_event(
            event_type='policy_prediction',
            data={
                'policy_type': policy.__class__.__name__,
                'predicted_action': prediction.get('action', 'unknown'),
                'confidence': prediction.get('confidence', 0.0),
                'model': self.extract_model_info(policy, tracker, domain)
            }
        )
    
    def track_form_execution(self, form, tracker, dispatcher, operation: str):
        """
        Track form execution event.
        
        Args:
            form: Rasa form object
            tracker: Rasa dialogue tracker
            dispatcher: Rasa dispatcher
            operation: Form operation (e.g., 'activate', 'validate', 'submit')
        """
        form_name = form.name() if hasattr(form, 'name') and callable(form.name) else str(form)
        self._emit_event(
            event_type='form_execution',
            data={
                'form_name': form_name,
                'form_type': form.__class__.__name__,
                'operation': operation,
                'model': self.extract_model_info(form, tracker, dispatcher)
            }
        )
    
    def track_slot_setting(self, tracker, slot_name: str, slot_value: str, source: str):
        """
        Track slot setting event.
        
        Args:
            tracker: Rasa dialogue tracker
            slot_name: Name of the slot
            slot_value: Value being set
            source: Source of the slot value (e.g., 'user', 'action')
        """
        self._emit_event(
            event_type='slot_setting',
            data={
                'sender_id': getattr(tracker, 'sender_id', 'unknown'),
                'slot_name': slot_name,
                'slot_value': slot_value,
                'source': source,
                'model': self.extract_model_info(tracker)
            }
        )
    
    def auto_track_agent(self, agent):
        """
        Automatically track a Rasa agent.
        
        Args:
            agent: Rasa agent object to track
            
        Returns:
            The agent object (for chaining)
        """
        self._tracked_agent = agent
        return agent


class DialogueTurnContext:
    """Context manager for tracking Rasa dialogue turn."""
    
    def __init__(self, tracker: RasaTracker, turn_id: str, model: str):
        """
        Initialize dialogue turn context.
        
        Args:
            tracker: Rasa tracker instance
            turn_id: Identifier for the dialogue turn
            model: Model being used
        """
        self.tracker = tracker
        self.turn_id = turn_id
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
            agent_name_suffix=f"turn:{self.turn_id}"
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
                agent_name_suffix=f"turn:{self.turn_id}"
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
                agent_name_suffix=f"turn:{self.turn_id}"
            )
        
        # Clean up
        self.tracker.cleanup_operation(self.operation_id)
    
    def log_intent_classification(self, intent_name: str, confidence: float):
        """Log an intent classification within this turn."""
        self.tracker.log_intent_classification(intent_name, confidence, self.operation_id)
    
    def log_entity_extraction(self, entity_type: str, entity_value: str):
        """Log an entity extraction within this turn."""
        self.tracker.log_entity_extraction(entity_type, entity_value, self.operation_id)
    
    def log_action_execution(self, action_name: str):
        """Log an action execution within this turn."""
        self.tracker.log_action_execution(action_name, self.operation_id)
    
    def log_slot_update(self, slot_name: str, slot_value: str):
        """Log a slot update within this turn."""
        self.tracker.log_slot_update(slot_name, slot_value, self.operation_id)


class ActionExecutionContext:
    """Context manager for tracking Rasa action execution."""
    
    def __init__(self, tracker: RasaTracker, action_name: str, model: str):
        """
        Initialize action execution context.
        
        Args:
            tracker: Rasa tracker instance
            action_name: Name of the action
            model: Model being used
        """
        self.tracker = tracker
        self.action_name = action_name
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
            agent_name_suffix=f"action:{self.action_name}"
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
                agent_name_suffix=f"action:{self.action_name}"
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
                agent_name_suffix=f"action:{self.action_name}"
            )
        
        # Clean up
        self.tracker.cleanup_operation(self.operation_id)
    
    def log_slot_update(self, slot_name: str, slot_value: str):
        """Log a slot update within this action."""
        self.tracker.log_slot_update(slot_name, slot_value, self.operation_id)
    
    def log_external_api_call(self, api_name: str):
        """Log an external API call within this action."""
        self.tracker.log_tool_call(f"api:{api_name}", self.operation_id)