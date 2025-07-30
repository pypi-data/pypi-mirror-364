"""LlamaIndex integration for Teraace Agentic Tracker.

LlamaIndex is a data framework for LLM applications that provides
tools for ingesting, structuring, and accessing data for use with LLMs.
It includes powerful agent capabilities for reasoning over data.
"""

import time
import uuid
from typing import Any, Dict, List, Optional, Union
from functools import wraps

from .base import BaseTracker


class LlamaIndexTracker(BaseTracker):
    """Tracker for LlamaIndex agents and data operations with workflow/crew support."""
    
    def __init__(
        self,
        workflow_name: Optional[str] = None,
        crew_name: Optional[str] = None,
        agent_name: Optional[str] = None,
        session_id: Optional[str] = None,
        config=None,
        run_env: str = "local",
        **metadata
    ):
        """Initialize LlamaIndex tracker with flexible workflow/crew/agent support."""
        # Store original parameters
        self.workflow_name = workflow_name
        self.crew_name = crew_name
        self.agent_name_only = agent_name
        self.metadata = metadata
        
        # Determine the primary identifier for tracking
        # Priority: workflow_name > crew_name > agent_name
        if workflow_name and agent_name:
            primary_name = f"{workflow_name}:{agent_name}"
        elif crew_name and agent_name:
            primary_name = f"{crew_name}:{agent_name}"
        elif workflow_name:
            primary_name = workflow_name
        elif crew_name:
            primary_name = crew_name
        elif agent_name:
            primary_name = agent_name
        else:
            primary_name = "llamaindex_workflow"
        
        # Initialize base tracker
        super().__init__(
            agent_name=primary_name,
            framework_name="llamaindex",
            session_id=session_id,
            config=config,
            run_env=run_env
        )
        
        # LlamaIndex-specific tracking state
        self._tracked_agents = {}
        self._tracked_indices = {}
    
    def track_agent_creation(self, agent: Any, tools: List[Any] = None, **kwargs) -> None:
        """Track LlamaIndex agent creation.
        
        Args:
            agent: The LlamaIndex agent instance
            tools: List of tools available to the agent
            **kwargs: Additional agent configuration
        """
        agent_data = {
            'agent_type': agent.__class__.__name__,
            'llm_model': getattr(getattr(agent, 'llm', None), 'model', 'unknown') if hasattr(agent, 'llm') else 'unknown',
            'tool_count': len(tools) if tools else 0,
            'tool_names': [getattr(tool, 'metadata', {}).get('name', tool.__class__.__name__) for tool in (tools or [])],
            'verbose': kwargs.get('verbose', False),
            'max_iterations': kwargs.get('max_iterations'),
            'callback_manager': hasattr(agent, 'callback_manager')
        }
        
        # Log agent creation as a tool call
        self.log_tool_call(f"create_agent_{agent_data['agent_type']}")
        
        # Store agent for tracking
        agent_id = id(agent)
        self._tracked_agents[agent_id] = agent
    
    def track_query_execution(self, agent: Any, query: str, response: Any = None) -> None:
        """Track query execution by the agent.
        
        Args:
            agent: The agent executing the query
            query: The query string
            response: The response from the agent
        """
        query_data = {
            'agent_type': agent.__class__.__name__,
            'query': query,
            'query_length': len(query),
            'has_response': response is not None,
            'response_type': type(response).__name__ if response else None,
            'response_text': str(response) if response else None
        }
        
        # Log query execution as a tool call
        self.log_tool_call(f"execute_query_{query_data['agent_type']}")
    
    def track_tool_execution(self, agent: Any, tool: Any, input_data: Any, output_data: Any = None) -> None:
        """Track tool execution by the agent.
        
        Args:
            agent: The agent using the tool
            tool: The tool being executed
            input_data: Input data passed to the tool
            output_data: Output from the tool execution
        """
        tool_data = {
            'agent_type': agent.__class__.__name__,
            'tool_name': getattr(tool, 'metadata', {}).get('name', tool.__class__.__name__),
            'tool_type': tool.__class__.__name__,
            'tool_description': getattr(tool, 'metadata', {}).get('description', ''),
            'input_type': type(input_data).__name__,
            'has_output': output_data is not None,
            'output_type': type(output_data).__name__ if output_data else None
        }
        
        # Log tool execution as a tool call
        self.log_tool_call(f"{tool_data['tool_name']}_{tool_data['agent_type']}")
    
    def track_index_creation(self, index: Any, documents: List[Any] = None, **kwargs) -> None:
        """Track index creation and document ingestion.
        
        Args:
            index: The LlamaIndex index instance
            documents: Documents used to create the index
            **kwargs: Additional index configuration
        """
        index_data = {
            'index_type': index.__class__.__name__,
            'document_count': len(documents) if documents else 0,
            'service_context': hasattr(index, 'service_context'),
            'storage_context': hasattr(index, 'storage_context'),
            'embed_model': getattr(getattr(index, 'service_context', None), 'embed_model', 'unknown') if hasattr(index, 'service_context') else 'unknown'
        }
        
        # Log index creation as a tool call
        self.log_tool_call(f"create_index_{index_data['index_type']}")
        
        # Store index for tracking
        index_id = id(index)
        self._tracked_indices[index_id] = index
    
    def track_retrieval_operation(self, retriever: Any, query: str, nodes: List[Any] = None) -> None:
        """Track retrieval operations from indices.
        
        Args:
            retriever: The retriever instance
            query: The retrieval query
            nodes: Retrieved nodes/chunks
        """
        retrieval_data = {
            'retriever_type': retriever.__class__.__name__,
            'query': query,
            'query_length': len(query),
            'retrieved_count': len(nodes) if nodes else 0,
            'similarity_top_k': getattr(retriever, 'similarity_top_k', None)
        }
        
        # Log retrieval operation as a tool call
        self.log_tool_call(f"retrieve_{retrieval_data['retriever_type']}")
    
    def track_synthesis_operation(self, synthesizer: Any, query: str, nodes: List[Any], response: Any = None) -> None:
        """Track response synthesis operations.
        
        Args:
            synthesizer: The response synthesizer
            query: The original query
            nodes: Nodes used for synthesis
            response: The synthesized response
        """
        synthesis_data = {
            'synthesizer_type': synthesizer.__class__.__name__,
            'query': query,
            'node_count': len(nodes) if nodes else 0,
            'has_response': response is not None,
            'response_length': len(str(response)) if response else 0
        }
        
        # Log synthesis operation as a tool call
        self.log_tool_call(f"synthesize_{synthesis_data['synthesizer_type']}")
    
    def track_reasoning_step(self, agent: Any, step_type: str, thought: str, action: str = None, observation: str = None) -> None:
        """Track reasoning steps in ReAct-style agents.
        
        Args:
            agent: The reasoning agent
            step_type: Type of reasoning step (thought, action, observation)
            thought: The agent's thought process
            action: Action taken by the agent
            observation: Observation from the action
        """
        reasoning_data = {
            'agent_type': agent.__class__.__name__,
            'step_type': step_type,
            'thought': thought,
            'action': action,
            'observation': observation,
            'thought_length': len(thought) if thought else 0
        }
        
        # Log reasoning step as a memory event
        self.log_memory_event("reasoning_step", f"{reasoning_data['step_type']}_{reasoning_data['agent_type']}")
    
    def track_memory_operation(self, memory: Any, operation: str, data: Any = None) -> None:
        """Track memory operations (chat memory, vector memory, etc.).
        
        Args:
            memory: The memory instance
            operation: Type of memory operation (put, get, clear)
            data: Data involved in the memory operation
        """
        memory_data = {
            'memory_type': memory.__class__.__name__,
            'operation': operation,
            'has_data': data is not None,
            'data_type': type(data).__name__ if data else None
        }
        
        # Log memory operation as a memory event
        self.log_memory_event("memory_operation", f"{memory_data['operation']}_{memory_data['memory_type']}")
    
    def auto_track_agent(self, agent: Any, tools: List[Any] = None) -> Any:
        """Automatically track a LlamaIndex agent.
        
        Args:
            agent: The LlamaIndex agent instance
            tools: Optional list of tools for the agent
            
        Returns:
            The same agent (for chaining)
        """
        agent_id = id(agent)
        self._tracked_agents[agent_id] = agent
        
        # Track agent creation
        self.track_agent_creation(agent, tools)
        
        return agent
    
    def auto_track_index(self, index: Any, documents: List[Any] = None) -> Any:
        """Automatically track a LlamaIndex index.
        
        Args:
            index: The LlamaIndex index instance
            documents: Optional documents used to create the index
            
        Returns:
            The same index (for chaining)
        """
        index_id = id(index)
        self._tracked_indices[index_id] = index
        
        # Track index creation
        self.track_index_creation(index, documents)
        
        return index
    
    def extract_model_info(self, *args, **kwargs) -> str:
        """Extract model information from LlamaIndex agent."""
        if args and hasattr(args[0], 'llm') and hasattr(args[0].llm, 'model'):
            return args[0].llm.model
        return kwargs.get('model', 'gpt-3.5-turbo')
    
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
    def auto_track_workflow_with_agents(cls, workflow_name: str, agent_names: List[str], **tracker_kwargs):
        """
        Automatically set up tracking for a LlamaIndex workflow with multiple agents.
        This is the easiest way to get started - just specify the workflow and agent names.
        """
        trackers = {}
        for agent_name in agent_names:
            tracker = cls(workflow_name=workflow_name, agent_name=agent_name, **tracker_kwargs)
            trackers[agent_name] = tracker
        
        return trackers if len(agent_names) > 1 else trackers[agent_names[0]]
    
    @classmethod
    def auto_track_crew_with_agents(cls, crew_name: str, agent_names: List[str], **tracker_kwargs):
        """
        Automatically set up tracking for a LlamaIndex crew with multiple agents.
        """
        trackers = {}
        for agent_name in agent_names:
            tracker = cls(crew_name=crew_name, agent_name=agent_name, **tracker_kwargs)
            trackers[agent_name] = tracker
        
        return trackers if len(agent_names) > 1 else trackers[agent_names[0]]


class WorkflowExecutionContext:
    """Context manager for tracking LlamaIndex workflow execution."""
    
    def __init__(self, tracker: LlamaIndexTracker, workflow_name: str, model: str):
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