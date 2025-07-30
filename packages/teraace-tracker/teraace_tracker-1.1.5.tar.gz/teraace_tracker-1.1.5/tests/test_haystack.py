"""Tests for Haystack integration."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from teraace_tracker.integrations.haystack import HaystackTracker


class TestHaystackTracker:
    """Test cases for HaystackTracker."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = HaystackTracker("test_agent")

    def test_initialization(self):
        """Test tracker initialization."""
        assert self.tracker.framework_name == "haystack"
        assert hasattr(self.tracker, 'emitter')

    def test_track_pipeline_execution(self):
        """Test pipeline execution tracking."""
        mock_pipeline = Mock()
        mock_pipeline.__class__.__name__ = "ExtractiveQAPipeline"
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_pipeline_execution(mock_pipeline, {"query": "test query"})
            
            # Verify event was emitted
            assert mock_emit.call_count >= 1
            call_args = mock_emit.call_args_list[0][1]
            assert call_args['event_type'] == 'pipeline_execution_start'
            assert call_args['data']['pipeline_type'] == 'ExtractiveQAPipeline'

    def test_track_node_processing(self):
        """Test node processing tracking."""
        mock_node = Mock()
        mock_node.__class__.__name__ = "DensePassageRetriever"
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_node_processing(mock_node, {"documents": []}, {"retrieved_docs": []})
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'node_processing'
            assert call_args['data']['node_type'] == 'DensePassageRetriever'

    def test_track_document_processing(self):
        """Test document processing tracking."""
        mock_processor = Mock()
        mock_processor.__class__.__name__ = "PreProcessor"
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_document_processing(mock_processor, [{"content": "test"}])
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'document_processing'
            assert call_args['data']['processor_type'] == 'PreProcessor'
            assert call_args['data']['document_count'] == 1

    def test_track_retriever_query(self):
        """Test retriever query tracking."""
        mock_retriever = Mock()
        mock_retriever.__class__.__name__ = "ElasticsearchRetriever"
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_retriever_query(mock_retriever, "test query", [{"content": "result"}])
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'retriever_query'
            assert call_args['data']['retriever_type'] == 'ElasticsearchRetriever'
            assert call_args['data']['query'] == 'test query'
            assert call_args['data']['result_count'] == 1

    def test_track_agent_step(self):
        """Test agent step tracking."""
        mock_agent = Mock()
        mock_agent.__class__.__name__ = "Agent"
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_agent_step(mock_agent, "reasoning", {"thought": "test"})
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'agent_step'
            assert call_args['data']['agent_type'] == 'Agent'
            assert call_args['data']['step_type'] == 'reasoning'

    def test_auto_track_pipeline(self):
        """Test automatic pipeline tracking."""
        mock_pipeline = Mock()
        
        # Test that auto_track_pipeline returns the pipeline
        result = self.tracker.auto_track_pipeline(mock_pipeline)
        assert result == mock_pipeline
        
        # Verify pipeline was stored
        assert hasattr(self.tracker, '_tracked_pipeline')
        assert self.tracker._tracked_pipeline == mock_pipeline