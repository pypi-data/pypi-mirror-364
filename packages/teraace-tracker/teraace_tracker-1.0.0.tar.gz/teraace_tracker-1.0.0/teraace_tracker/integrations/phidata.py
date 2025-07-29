"""Phidata integration for Teraace Agentic Tracker.

Phidata is a framework for building AI assistants with memory, knowledge,
and tools. It focuses on production-ready AI applications.
"""

from typing import Any, Dict, List, Optional, Union
from .base import BaseTracker


class PhidataTracker(BaseTracker):
    """Tracker for Phidata AI assistants."""
    
    def __init__(self, agent_name: str = "phidata_agent", **kwargs):
        """Initialize Phidata tracker."""
        super().__init__(agent_name=agent_name, framework_name="phidata", **kwargs)
        self._tracked_assistants = {}
        self._session_data = {}
    
    def track_assistant_creation(self, assistant: Any, config: Dict[str, Any]) -> None:
        """Track assistant creation and configuration.
        
        Args:
            assistant: The Phidata assistant instance
            config: Configuration used to create the assistant
        """
        assistant_data = {
            'assistant_id': getattr(assistant, 'id', None),
            'assistant_name': getattr(assistant, 'name', 'unknown'),
            'assistant_type': assistant.__class__.__name__,
            'model': getattr(assistant, 'model', None),
            'provider': getattr(assistant, 'provider', None),
            'temperature': getattr(assistant, 'temperature', None),
            'max_tokens': getattr(assistant, 'max_tokens', None),
            'has_memory': hasattr(assistant, 'memory') and assistant.memory is not None,
            'has_knowledge': hasattr(assistant, 'knowledge') and assistant.knowledge is not None,
            'tool_count': len(getattr(assistant, 'tools', []))
        }
        
        self._emit_event(
            event_type='assistant_creation',
            data=assistant_data,
            metadata={'framework': self.framework_name}
        )
        
        # Store assistant for session tracking
        assistant_id = id(assistant)
        self._tracked_assistants[assistant_id] = assistant
    
    def track_conversation_run(self, assistant: Any, message: str, session_id: Optional[str] = None) -> None:
        """Track a conversation run with the assistant.
        
        Args:
            assistant: The assistant handling the conversation
            message: The user message
            session_id: Optional session identifier
        """
        run_data = {
            'assistant_name': getattr(assistant, 'name', 'unknown'),
            'assistant_type': assistant.__class__.__name__,
            'message': message,
            'session_id': session_id,
            'has_memory': hasattr(assistant, 'memory') and assistant.memory is not None,
            'message_length': len(message)
        }
        
        self._emit_event(
            event_type='conversation_run_start',
            data=run_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_tool_execution(self, assistant: Any, tool: Any, function_name: str, arguments: Dict[str, Any], result: Any = None) -> None:
        """Track tool execution by the assistant.
        
        Args:
            assistant: The assistant executing the tool
            tool: The tool being executed
            function_name: Name of the function being called
            arguments: Arguments passed to the function
            result: Result of the tool execution
        """
        tool_data = {
            'assistant_name': getattr(assistant, 'name', 'unknown'),
            'tool_name': getattr(tool, 'name', tool.__class__.__name__),
            'tool_type': tool.__class__.__name__,
            'function_name': function_name,
            'arguments': arguments,
            'has_result': result is not None,
            'result_type': type(result).__name__ if result is not None else None
        }
        
        self._emit_event(
            event_type='tool_execution',
            data=tool_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_memory_operation(self, assistant: Any, operation: str, data: Dict[str, Any]) -> None:
        """Track memory operations (save, retrieve, update).
        
        Args:
            assistant: The assistant performing the memory operation
            operation: Type of memory operation (save, retrieve, update, delete)
            data: Data related to the memory operation
        """
        memory_data = {
            'assistant_name': getattr(assistant, 'name', 'unknown'),
            'memory_type': getattr(assistant.memory, '__class__.__name__', 'unknown') if hasattr(assistant, 'memory') else None,
            'operation': operation,
            'data_keys': list(data.keys()) if isinstance(data, dict) else [],
            'data_size': len(str(data))
        }
        
        self._emit_event(
            event_type='memory_operation',
            data=memory_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_knowledge_query(self, assistant: Any, query: str, results: List[Any]) -> None:
        """Track knowledge base queries.
        
        Args:
            assistant: The assistant querying knowledge
            query: The search query
            results: Results from the knowledge base
        """
        knowledge_data = {
            'assistant_name': getattr(assistant, 'name', 'unknown'),
            'knowledge_type': getattr(assistant.knowledge, '__class__.__name__', 'unknown') if hasattr(assistant, 'knowledge') else None,
            'query': query,
            'result_count': len(results),
            'query_length': len(query)
        }
        
        self._emit_event(
            event_type='knowledge_query',
            data=knowledge_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_workflow_execution(self, workflow: Any, inputs: Dict[str, Any], outputs: Dict[str, Any] = None) -> None:
        """Track workflow execution.
        
        Args:
            workflow: The workflow being executed
            inputs: Input data for the workflow
            outputs: Output data from the workflow
        """
        workflow_data = {
            'workflow_name': getattr(workflow, 'name', 'unknown'),
            'workflow_type': workflow.__class__.__name__,
            'input_keys': list(inputs.keys()) if isinstance(inputs, dict) else [],
            'output_keys': list(outputs.keys()) if isinstance(outputs, dict) and outputs else [],
            'has_outputs': outputs is not None
        }
        
        self._emit_event(
            event_type='workflow_execution',
            data=workflow_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_session_management(self, assistant: Any, session_id: str, operation: str) -> None:
        """Track session management operations.
        
        Args:
            assistant: The assistant managing the session
            session_id: The session identifier
            operation: Type of session operation (create, update, delete, retrieve)
        """
        session_data = {
            'assistant_name': getattr(assistant, 'name', 'unknown'),
            'session_id': session_id,
            'operation': operation,
            'session_count': len(self._session_data)
        }
        
        self._emit_event(
            event_type='session_management',
            data=session_data,
            metadata={'framework': self.framework_name}
        )
        
        # Update session tracking
        if operation == 'create':
            self._session_data[session_id] = {'created': True, 'assistant': assistant}
        elif operation == 'delete' and session_id in self._session_data:
            del self._session_data[session_id]
    
    def auto_track_assistant(self, assistant: Any) -> Any:
        """Automatically track a Phidata assistant.
        
        Args:
            assistant: The Phidata assistant instance
            
        Returns:
            The same assistant (for chaining)
        """
        assistant_id = id(assistant)
        self._tracked_assistants[assistant_id] = assistant
        
        # Track assistant creation
        config = {
            'model': getattr(assistant, 'model', None),
            'provider': getattr(assistant, 'provider', None),
            'temperature': getattr(assistant, 'temperature', None)
        }
        self.track_assistant_creation(assistant, config)
        
        return assistant
    
    def extract_model_info(self, *args, **kwargs) -> str:
        """Extract model information from Phidata assistant."""
        if args and hasattr(args[0], 'model'):
            return args[0].model
        return kwargs.get('model', 'gpt-4')
    
    def _emit_event(self, event_type: str, data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Emit a tracking event."""
        # This is a placeholder - in a real implementation, this would emit to the tracking system
        pass