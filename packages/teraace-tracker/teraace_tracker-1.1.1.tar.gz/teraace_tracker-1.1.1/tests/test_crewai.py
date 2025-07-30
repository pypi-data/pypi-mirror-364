"""
Tests for CrewAI integration.
"""

import pytest
import time
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

from teraace_tracker.integrations.crewai import CrewAITracker, TaskExecutionContext
from teraace_tracker.config import Config


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    with patch.dict('os.environ', {'TERAACE_API_KEY': 'test_key'}):
        return Config()


class TestCrewAITracker:
    """Tests for CrewAITracker class."""
    
    def test_tracker_initialization(self, mock_config):
        """Test tracker initialization."""
        tracker = CrewAITracker(
            agent_name="test_crew_agent",
            session_id="test_session",
            config=mock_config
        )
        
        assert tracker.agent_name == "test_crew_agent"
        assert tracker.session_id == "test_session"
        assert tracker.run_env == "local"
        assert tracker.emitter is not None
    
    def test_tracker_auto_session_id(self, mock_config):
        """Test automatic session ID generation."""
        tracker = CrewAITracker(
            agent_name="test_crew_agent",
            config=mock_config
        )
        
        assert tracker.session_id is not None
        assert len(tracker.session_id) > 0
    
    def test_track_agent_execution_decorator_success(self, mock_config):
        """Test agent execution tracking decorator for successful execution."""
        tracker = CrewAITracker("test_agent", config=mock_config)
        tracker.emitter.emit_agent_event = MagicMock()
        
        @tracker.track_agent_execution
        def test_function(arg1, arg2, model="gpt-4o"):
            time.sleep(0.1)
            return f"result: {arg1} {arg2}"
        
        result = test_function("hello", "world")
        
        assert result == "result: hello world"
        
        # Should emit start and end events
        assert tracker.emitter.emit_agent_event.call_count == 2
        
        # Check start event
        start_call = tracker.emitter.emit_agent_event.call_args_list[0][1]
        assert start_call["agent_name"] == "test_agent"
        assert start_call["agent_framework"] == "crewai"
        assert start_call["event_type"] == "start"
        assert start_call["success"] is True
        
        # Check end event
        end_call = tracker.emitter.emit_agent_event.call_args_list[1][1]
        assert end_call["event_type"] == "end"
        assert end_call["success"] is True
        assert end_call["duration_ms"] >= 100  # At least 100ms due to sleep
    
    def test_track_agent_execution_decorator_error(self, mock_config):
        """Test agent execution tracking decorator for error case."""
        tracker = CrewAITracker("test_agent", config=mock_config)
        tracker.emitter.emit_agent_event = MagicMock()
        
        @tracker.track_agent_execution
        def failing_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            failing_function()
        
        # Should emit start and error events
        assert tracker.emitter.emit_agent_event.call_count == 2
        
        # Check error event
        error_call = tracker.emitter.emit_agent_event.call_args_list[1][1]
        assert error_call["event_type"] == "error"
        assert error_call["success"] is False
        assert error_call["exception"] == "ValueError"
    
    def test_task_execution_context_success(self, mock_config):
        """Test task execution context manager for successful execution."""
        tracker = CrewAITracker("test_agent", config=mock_config)
        tracker.emitter.emit_agent_event = MagicMock()
        
        with tracker.track_task_execution("test_task", "gpt-4o") as task_context:
            task_context.log_tool_call("test_tool")
            task_context.log_memory_event("read", "test_key")
            time.sleep(0.1)
        
        # Should emit start and end events
        assert tracker.emitter.emit_agent_event.call_count == 2
        
        # Check start event
        start_call = tracker.emitter.emit_agent_event.call_args_list[0][1]
        assert start_call["agent_name"] == "test_agent:test_task"
        assert start_call["event_type"] == "start"
        assert start_call["model"] == "gpt-4o"
        
        # Check end event
        end_call = tracker.emitter.emit_agent_event.call_args_list[1][1]
        assert end_call["event_type"] == "end"
        assert end_call["success"] is True
        assert len(end_call["tool_calls"]) == 1
        assert len(end_call["memory_events"]) == 1
    
    def test_task_execution_context_error(self, mock_config):
        """Test task execution context manager for error case."""
        tracker = CrewAITracker("test_agent", config=mock_config)
        tracker.emitter.emit_agent_event = MagicMock()
        
        with pytest.raises(RuntimeError):
            with tracker.track_task_execution("test_task", "gpt-4o"):
                raise RuntimeError("Test error")
        
        # Should emit start and error events
        assert tracker.emitter.emit_agent_event.call_count == 2
        
        # Check error event
        error_call = tracker.emitter.emit_agent_event.call_args_list[1][1]
        assert error_call["event_type"] == "error"
        assert error_call["success"] is False
        assert error_call["exception"] == "RuntimeError"
    
    def test_log_tool_call(self, mock_config):
        """Test logging tool calls."""
        tracker = CrewAITracker("test_agent", config=mock_config)
        tracker.emitter.create_tool_call = MagicMock()
        
        tracker.log_tool_call("test_tool")
        
        tracker.emitter.create_tool_call.assert_called_once_with("test_tool")
    
    def test_log_memory_event(self, mock_config):
        """Test logging memory events."""
        tracker = CrewAITracker("test_agent", config=mock_config)
        tracker.emitter.create_memory_event = MagicMock()
        
        tracker.log_memory_event("read", "test_key")
        
        tracker.emitter.create_memory_event.assert_called_once_with("read", "test_key")
    
    def test_extract_model_info(self, mock_config):
        """Test model information extraction."""
        tracker = CrewAITracker("test_agent", config=mock_config)
        
        # Test direct model in kwargs
        model = tracker._extract_model_info((), {"model": "gpt-4o"})
        assert model == "gpt-4o"
        
        # Test LLM object in kwargs
        mock_llm = MagicMock()
        mock_llm.model_name = "claude-3"
        model = tracker._extract_model_info((), {"llm": mock_llm})
        assert model == "claude-3"
        
        # Test agent object in args
        mock_agent = MagicMock()
        mock_agent.llm.model_name = "gpt-3.5"
        model = tracker._extract_model_info((mock_agent,), {})
        assert model == "gpt-3.5"
        
        # Test unknown case
        model = tracker._extract_model_info((), {})
        assert model == "unknown"
    
    @pytest.mark.asyncio
    async def test_flush_events(self, mock_config):
        """Test manual event flushing."""
        tracker = CrewAITracker("test_agent", config=mock_config)
        tracker.emitter.flush_events = AsyncMock(return_value=True)
        
        result = await tracker.flush_events()
        
        assert result is True
        tracker.emitter.flush_events.assert_called_once()
    
    def test_get_buffer_size(self, mock_config):
        """Test getting buffer size."""
        tracker = CrewAITracker("test_agent", config=mock_config)
        tracker.emitter.get_buffer_size = MagicMock(return_value=5)
        
        size = tracker.get_buffer_size()
        
        assert size == 5
        tracker.emitter.get_buffer_size.assert_called_once()


class TestTaskExecutionContext:
    """Tests for TaskExecutionContext class."""
    
    def test_context_manager_lifecycle(self, mock_config):
        """Test context manager enter and exit lifecycle."""
        tracker = CrewAITracker("test_agent", config=mock_config)
        tracker.emitter.emit_agent_event = MagicMock()
        
        context = TaskExecutionContext(tracker, "test_task", "gpt-4o")
        
        # Test enter
        result = context.__enter__()
        assert result is context
        assert context.start_time is not None
        
        # Test exit without exception
        context.__exit__(None, None, None)
        
        # Should have emitted start and end events
        assert tracker.emitter.emit_agent_event.call_count == 2
    
    def test_context_manager_with_exception(self, mock_config):
        """Test context manager with exception handling."""
        tracker = CrewAITracker("test_agent", config=mock_config)
        tracker.emitter.emit_agent_event = MagicMock()
        
        context = TaskExecutionContext(tracker, "test_task", "gpt-4o")
        context.__enter__()
        
        # Test exit with exception
        context.__exit__(ValueError, ValueError("test"), None)
        
        # Should have emitted start and error events
        assert tracker.emitter.emit_agent_event.call_count == 2
        
        # Check error event
        error_call = tracker.emitter.emit_agent_event.call_args_list[1][1]
        assert error_call["event_type"] == "error"
        assert error_call["success"] is False
        assert error_call["exception"] == "ValueError"