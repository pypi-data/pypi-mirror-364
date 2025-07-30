"""Tests for LlamaIndex integration."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from teraace_tracker.integrations.llamaindex import LlamaIndexTracker


class TestLlamaIndexTracker:
    """Test cases for LlamaIndexTracker."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = LlamaIndexTracker()

    def test_initialization(self):
        """Test tracker initialization."""
        assert self.tracker.framework_name == "llamaindex"
        assert hasattr(self.tracker, 'emitter')
        assert hasattr(self.tracker, '_tracked_agents')
        assert hasattr(self.tracker, '_tracked_indices')

    def test_track_agent_creation(self):
        """Test agent creation tracking."""
        mock_agent = Mock()
        mock_agent.__class__.__name__ = "ReActAgent"
        mock_agent.llm = Mock()
        mock_agent.llm.model = "gpt-4"
        mock_agent.callback_manager = True
        
        mock_tool1 = Mock()
        mock_tool1.metadata = {"name": "calculator", "description": "Math tool"}
        mock_tool2 = Mock()
        mock_tool2.metadata = {"name": "search", "description": "Web search"}
        
        tools = [mock_tool1, mock_tool2]
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_agent_creation(
                agent=mock_agent,
                tools=tools,
                verbose=True,
                max_iterations=10
            )
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'agent_creation'
            assert call_args['data']['agent_type'] == 'ReActAgent'
            assert call_args['data']['tool_count'] == 2
            assert 'calculator' in call_args['data']['tool_names']

    def test_track_query_execution(self):
        """Test query execution tracking."""
        mock_agent = Mock()
        mock_agent.__class__.__name__ = "QueryEngine"
        
        query = "What is the capital of France?"
        response = "The capital of France is Paris."
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_query_execution(mock_agent, query, response)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'query_execution_start'
            assert call_args['data']['query'] == query
            assert call_args['data']['response_text'] == response

    def test_track_tool_execution(self):
        """Test tool execution tracking."""
        mock_agent = Mock()
        mock_agent.__class__.__name__ = "ReActAgent"
        
        mock_tool = Mock()
        mock_tool.metadata = {"name": "calculator", "description": "Math calculations"}
        mock_tool.__class__.__name__ = "CalculatorTool"
        
        input_data = {"expression": "2 + 2"}
        output_data = {"result": 4}
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_tool_execution(mock_agent, mock_tool, input_data, output_data)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'tool_execution'
            assert call_args['data']['tool_name'] == 'calculator'
            assert call_args['data']['tool_type'] == 'CalculatorTool'

    def test_track_index_creation(self):
        """Test index creation tracking."""
        mock_index = Mock()
        mock_index.__class__.__name__ = "VectorStoreIndex"
        mock_index.service_context = True
        mock_index.storage_context = True
        
        mock_doc1 = Mock()
        mock_doc2 = Mock()
        documents = [mock_doc1, mock_doc2]
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_index_creation(mock_index, documents)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'index_creation'
            assert call_args['data']['index_type'] == 'VectorStoreIndex'
            assert call_args['data']['document_count'] == 2

    def test_track_retrieval_operation(self):
        """Test retrieval operation tracking."""
        mock_retriever = Mock()
        mock_retriever.__class__.__name__ = "VectorIndexRetriever"
        mock_retriever.similarity_top_k = 5
        
        query = "machine learning"
        nodes = [Mock(), Mock(), Mock()]
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_retrieval_operation(mock_retriever, query, nodes)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'retrieval_operation'
            assert call_args['data']['query'] == query
            assert call_args['data']['retrieved_count'] == 3

    def test_track_synthesis_operation(self):
        """Test synthesis operation tracking."""
        mock_synthesizer = Mock()
        mock_synthesizer.__class__.__name__ = "ResponseSynthesizer"
        
        query = "What is AI?"
        nodes = [Mock(), Mock()]
        response = "AI is artificial intelligence..."
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_synthesis_operation(mock_synthesizer, query, nodes, response)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'synthesis_operation'
            assert call_args['data']['query'] == query
            assert call_args['data']['node_count'] == 2

    def test_track_reasoning_step(self):
        """Test reasoning step tracking."""
        mock_agent = Mock()
        mock_agent.__class__.__name__ = "ReActAgent"
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_reasoning_step(
                agent=mock_agent,
                step_type="thought",
                thought="I need to calculate 2+2",
                action="use_calculator",
                observation="Result is 4"
            )
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'reasoning_step'
            assert call_args['data']['step_type'] == 'thought'
            assert call_args['data']['thought'] == 'I need to calculate 2+2'

    def test_track_memory_operation(self):
        """Test memory operation tracking."""
        mock_memory = Mock()
        mock_memory.__class__.__name__ = "ChatMemoryBuffer"
        
        data = {"message": "Hello", "role": "user"}
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_memory_operation(mock_memory, "put", data)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'memory_operation'
            assert call_args['data']['memory_type'] == 'ChatMemoryBuffer'
            assert call_args['data']['operation'] == 'put'

    def test_auto_track_agent(self):
        """Test automatic agent tracking."""
        mock_agent = Mock()
        mock_agent.__class__.__name__ = "ReActAgent"
        
        mock_tool = Mock()
        mock_tool.metadata = {"name": "test_tool"}
        tools = [mock_tool]
        
        with patch.object(self.tracker, 'track_agent_creation') as mock_track:
            result = self.tracker.auto_track_agent(mock_agent, tools)
            
            # Verify agent was tracked
            mock_track.assert_called_once_with(mock_agent, tools)
            assert result == mock_agent
            
            # Verify agent was stored
            agent_id = id(mock_agent)
            assert agent_id in self.tracker._tracked_agents

    def test_auto_track_index(self):
        """Test automatic index tracking."""
        mock_index = Mock()
        mock_index.__class__.__name__ = "VectorStoreIndex"
        
        documents = [Mock(), Mock()]
        
        with patch.object(self.tracker, 'track_index_creation') as mock_track:
            result = self.tracker.auto_track_index(mock_index, documents)
            
            # Verify index was tracked
            mock_track.assert_called_once_with(mock_index, documents)
            assert result == mock_index
            
            # Verify index was stored
            index_id = id(mock_index)
            assert index_id in self.tracker._tracked_indices