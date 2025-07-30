"""Tests for Semantic Kernel integration."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from teraace_tracker.integrations.semantic_kernel import SemanticKernelTracker


class TestSemanticKernelTracker:
    """Test cases for SemanticKernelTracker."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = SemanticKernelTracker("test_agent")

    def test_initialization(self):
        """Test tracker initialization."""
        assert self.tracker.framework_name == "semantic_kernel"
        assert hasattr(self.tracker, 'emitter')

    def test_track_kernel_execution(self):
        """Test kernel execution tracking."""
        # Mock kernel and function
        mock_kernel = Mock()
        mock_function = Mock()
        mock_function.name = "test_function"
        mock_function.skill_name = "test_skill"
        
        # Mock the execution
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_kernel_execution(mock_kernel, mock_function, {"input": "test"})
            
            # Verify event was emitted
            assert mock_emit.call_count >= 1
            call_args = mock_emit.call_args_list[0][1]
            assert call_args['event_type'] == 'kernel_execution_start'
            assert call_args['data']['function_name'] == 'test_function'
            assert call_args['data']['skill_name'] == 'test_skill'

    def test_track_planner_operation(self):
        """Test planner operation tracking."""
        mock_planner = Mock()
        mock_planner.__class__.__name__ = "SequentialPlanner"
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_planner_operation(mock_planner, "create_plan", {"goal": "test goal"})
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'planner_operation'
            assert call_args['data']['planner_type'] == 'SequentialPlanner'
            assert call_args['data']['operation'] == 'create_plan'

    def test_track_memory_operation(self):
        """Test memory operation tracking."""
        mock_memory = Mock()
        mock_memory.__class__.__name__ = "VolatileMemoryStore"
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_memory_operation(mock_memory, "save", {"key": "test", "value": "data"})
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'memory_operation'
            assert call_args['data']['memory_type'] == 'VolatileMemoryStore'
            assert call_args['data']['operation'] == 'save'

    def test_track_connector_call(self):
        """Test connector call tracking."""
        mock_connector = Mock()
        mock_connector.__class__.__name__ = "OpenAIConnector"
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_connector_call(mock_connector, "complete", {"prompt": "test"})
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'connector_call'
            assert call_args['data']['connector_type'] == 'OpenAIConnector'
            assert call_args['data']['method'] == 'complete'

    def test_auto_track_kernel(self):
        """Test automatic kernel tracking."""
        mock_kernel = Mock()
        
        # Test that auto_track_kernel returns the kernel
        result = self.tracker.auto_track_kernel(mock_kernel)
        assert result == mock_kernel
        
        # Verify kernel was stored
        assert hasattr(self.tracker, '_tracked_kernel')
        assert self.tracker._tracked_kernel == mock_kernel