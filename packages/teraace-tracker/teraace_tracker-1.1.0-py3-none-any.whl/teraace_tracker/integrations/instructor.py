"""Instructor integration for Teraace Agentic Tracker.

Instructor is a Python library that makes it easy to get structured data
from Large Language Models (LLMs) like GPT-3.5, GPT-4, etc.
"""

from typing import Any, Dict, List, Optional, Union
from .base import BaseTracker


class InstructorTracker(BaseTracker):
    """Tracker for Instructor structured data extraction."""
    
    def __init__(self, agent_name: str = "instructor_agent", **kwargs):
        """Initialize Instructor tracker."""
        super().__init__(agent_name=agent_name, framework_name="instructor", **kwargs)
        self._tracked_clients = {}
        self._extraction_history = []
    
    def track_client_creation(self, client: Any, client_config: Dict[str, Any]) -> None:
        """Track Instructor client creation.
        
        Args:
            client: The Instructor client instance
            client_config: Configuration for the client
        """
        client_data = {
            'client_type': client.__class__.__name__,
            'base_client': client_config.get('base_client', 'openai'),
            'mode': client_config.get('mode', 'function_call'),
            'max_retries': client_config.get('max_retries', 3),
            'validation_context': client_config.get('validation_context', False)
        }
        
        self._emit_event(
            event_type='client_creation',
            data=client_data,
            metadata={'framework': self.framework_name}
        )
        
        # Store client for tracking
        client_id = id(client)
        self._tracked_clients[client_id] = client
    
    def track_extraction_start(self, client: Any, response_model: Any, messages: List[Dict[str, Any]], **kwargs) -> None:
        """Track start of structured data extraction.
        
        Args:
            client: The Instructor client
            response_model: Pydantic model for response structure
            messages: Messages sent to the model
            **kwargs: Additional parameters
        """
        extraction_data = {
            'client_type': client.__class__.__name__,
            'response_model': response_model.__name__ if hasattr(response_model, '__name__') else str(response_model),
            'message_count': len(messages),
            'model': kwargs.get('model', 'unknown'),
            'temperature': kwargs.get('temperature'),
            'max_tokens': kwargs.get('max_tokens'),
            'stream': kwargs.get('stream', False),
            'validation_context': kwargs.get('validation_context', False)
        }
        
        self._emit_event(
            event_type='extraction_start',
            data=extraction_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_schema_validation(self, response_model: Any, raw_response: str, validation_result: Dict[str, Any]) -> None:
        """Track schema validation of extracted data.
        
        Args:
            response_model: The Pydantic model used for validation
            raw_response: Raw response from the model
            validation_result: Result of validation process
        """
        validation_data = {
            'model_name': response_model.__name__ if hasattr(response_model, '__name__') else str(response_model),
            'raw_response_length': len(raw_response),
            'validation_successful': validation_result.get('successful', False),
            'field_count': validation_result.get('field_count', 0),
            'required_fields': validation_result.get('required_fields', []),
            'optional_fields': validation_result.get('optional_fields', []),
            'validation_errors': validation_result.get('errors', []),
            'error_count': len(validation_result.get('errors', []))
        }
        
        self._emit_event(
            event_type='schema_validation',
            data=validation_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_retry_attempt(self, client: Any, attempt_number: int, error: str, retry_strategy: str) -> None:
        """Track retry attempts during extraction.
        
        Args:
            client: The Instructor client
            attempt_number: Current retry attempt number
            error: Error that triggered the retry
            retry_strategy: Strategy used for retry
        """
        retry_data = {
            'client_type': client.__class__.__name__,
            'attempt_number': attempt_number,
            'error_type': type(error).__name__ if isinstance(error, Exception) else 'string',
            'error_message': str(error),
            'retry_strategy': retry_strategy,
            'is_validation_error': 'validation' in str(error).lower()
        }
        
        self._emit_event(
            event_type='retry_attempt',
            data=retry_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_function_call_mode(self, client: Any, function_schema: Dict[str, Any], function_call_result: Dict[str, Any]) -> None:
        """Track function calling mode usage.
        
        Args:
            client: The Instructor client
            function_schema: Schema of the function call
            function_call_result: Result from function call
        """
        function_data = {
            'client_type': client.__class__.__name__,
            'function_name': function_schema.get('name', 'unknown'),
            'parameter_count': len(function_schema.get('parameters', {}).get('properties', {})),
            'required_params': function_schema.get('parameters', {}).get('required', []),
            'call_successful': function_call_result.get('successful', False),
            'arguments_provided': function_call_result.get('arguments', {}),
            'result_type': type(function_call_result.get('result')).__name__ if function_call_result.get('result') else None
        }
        
        self._emit_event(
            event_type='function_call_mode',
            data=function_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_streaming_extraction(self, client: Any, partial_results: List[Any], final_result: Any) -> None:
        """Track streaming extraction process.
        
        Args:
            client: The Instructor client
            partial_results: List of partial results during streaming
            final_result: Final complete result
        """
        streaming_data = {
            'client_type': client.__class__.__name__,
            'partial_count': len(partial_results),
            'has_final_result': final_result is not None,
            'final_result_type': type(final_result).__name__ if final_result else None,
            'streaming_successful': final_result is not None,
            'avg_partial_size': sum(len(str(p)) for p in partial_results) / len(partial_results) if partial_results else 0
        }
        
        self._emit_event(
            event_type='streaming_extraction',
            data=streaming_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_extraction_completion(self, client: Any, response_model: Any, final_result: Any, extraction_stats: Dict[str, Any]) -> None:
        """Track completion of data extraction.
        
        Args:
            client: The Instructor client
            response_model: The response model used
            final_result: Final extracted and validated result
            extraction_stats: Statistics about the extraction process
        """
        completion_data = {
            'client_type': client.__class__.__name__,
            'response_model': response_model.__name__ if hasattr(response_model, '__name__') else str(response_model),
            'extraction_successful': final_result is not None,
            'result_type': type(final_result).__name__ if final_result else None,
            'total_attempts': extraction_stats.get('total_attempts', 1),
            'total_tokens': extraction_stats.get('total_tokens', 0),
            'extraction_time': extraction_stats.get('extraction_time'),
            'validation_passed': extraction_stats.get('validation_passed', False),
            'cost_estimate': extraction_stats.get('cost_estimate')
        }
        
        self._emit_event(
            event_type='extraction_completion',
            data=completion_data,
            metadata={'framework': self.framework_name}
        )
        
        # Store in extraction history
        self._extraction_history.append(completion_data)
    
    def track_batch_extraction(self, client: Any, batch_size: int, batch_results: List[Any], batch_stats: Dict[str, Any]) -> None:
        """Track batch extraction operations.
        
        Args:
            client: The Instructor client
            batch_size: Size of the batch
            batch_results: Results from batch processing
            batch_stats: Statistics about batch processing
        """
        batch_data = {
            'client_type': client.__class__.__name__,
            'batch_size': batch_size,
            'successful_extractions': len([r for r in batch_results if r is not None]),
            'failed_extractions': len([r for r in batch_results if r is None]),
            'success_rate': len([r for r in batch_results if r is not None]) / batch_size if batch_size > 0 else 0,
            'total_tokens': batch_stats.get('total_tokens', 0),
            'avg_tokens_per_item': batch_stats.get('total_tokens', 0) / batch_size if batch_size > 0 else 0,
            'batch_processing_time': batch_stats.get('processing_time')
        }
        
        self._emit_event(
            event_type='batch_extraction',
            data=batch_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_model_usage(self, client: Any, model_name: str, usage_stats: Dict[str, Any]) -> None:
        """Track model usage statistics.
        
        Args:
            client: The Instructor client
            model_name: Name of the model used
            usage_stats: Usage statistics
        """
        usage_data = {
            'client_type': client.__class__.__name__,
            'model_name': model_name,
            'prompt_tokens': usage_stats.get('prompt_tokens', 0),
            'completion_tokens': usage_stats.get('completion_tokens', 0),
            'total_tokens': usage_stats.get('total_tokens', 0),
            'requests_made': usage_stats.get('requests_made', 1),
            'avg_tokens_per_request': usage_stats.get('total_tokens', 0) / usage_stats.get('requests_made', 1),
            'estimated_cost': usage_stats.get('estimated_cost')
        }
        
        self._emit_event(
            event_type='model_usage',
            data=usage_data,
            metadata={'framework': self.framework_name}
        )
    
    def auto_track_client(self, client: Any, config: Dict[str, Any] = None) -> Any:
        """Automatically track an Instructor client.
        
        Args:
            client: The Instructor client instance
            config: Optional client configuration
            
        Returns:
            The same client (for chaining)
        """
        client_id = id(client)
        self._tracked_clients[client_id] = client
        
        # Track client creation if config is provided
        if config:
            self.track_client_creation(client, config)
        
        return client
    
    def extract_model_info(self, *args, **kwargs) -> str:
        """Extract model information from Instructor client."""
        return kwargs.get('model', 'gpt-3.5-turbo')
    
    def _emit_event(self, event_type: str, data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Emit a tracking event."""
        # This is a placeholder - in a real implementation, this would emit to the tracking system
        pass