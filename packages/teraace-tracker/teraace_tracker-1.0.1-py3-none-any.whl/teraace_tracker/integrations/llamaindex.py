"""LlamaIndex integration for Teraace Agentic Tracker.

LlamaIndex is a data framework for LLM applications that provides
tools for ingesting, structuring, and accessing data for use with LLMs.
It includes powerful agent capabilities for reasoning over data.
"""

from typing import Any, Dict, List, Optional, Union
from .base import BaseTracker


class LlamaIndexTracker(BaseTracker):
    """Tracker for LlamaIndex agents and data operations."""
    
    def __init__(self, agent_name: str = "llamaindex_agent", **kwargs):
        """Initialize LlamaIndex tracker."""
        super().__init__(agent_name=agent_name, framework_name="llamaindex", **kwargs)
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
        
        self._emit_event(
            event_type='agent_creation',
            data=agent_data,
            metadata={'framework': self.framework_name}
        )
        
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
        
        self._emit_event(
            event_type='query_execution_start',
            data=query_data,
            metadata={'framework': self.framework_name}
        )
    
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
        
        self._emit_event(
            event_type='tool_execution',
            data=tool_data,
            metadata={'framework': self.framework_name}
        )
    
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
        
        self._emit_event(
            event_type='index_creation',
            data=index_data,
            metadata={'framework': self.framework_name}
        )
        
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
        
        self._emit_event(
            event_type='retrieval_operation',
            data=retrieval_data,
            metadata={'framework': self.framework_name}
        )
    
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
        
        self._emit_event(
            event_type='synthesis_operation',
            data=synthesis_data,
            metadata={'framework': self.framework_name}
        )
    
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
        
        self._emit_event(
            event_type='reasoning_step',
            data=reasoning_data,
            metadata={'framework': self.framework_name}
        )
    
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
        
        self._emit_event(
            event_type='memory_operation',
            data=memory_data,
            metadata={'framework': self.framework_name}
        )
    
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
    
    def _emit_event(self, event_type: str, data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Emit a tracking event."""
        # This is a placeholder - in a real implementation, this would emit to the tracking system
        pass