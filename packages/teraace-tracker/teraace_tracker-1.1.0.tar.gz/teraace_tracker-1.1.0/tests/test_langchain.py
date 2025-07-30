"""
Tests for LangChain integration.
"""

import pytest
import uuid
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

from teraace_tracker.integrations.langchain import LangChainTracker
from teraace_tracker.config import Config


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    with patch.dict('os.environ', {'TERAACE_API_KEY': 'test_key'}):
        return Config()


class TestLangChainTracker:
    """Tests for LangChainTracker class."""
    
    def test_tracker_initialization(self, mock_config):
        """Test tracker initialization."""
        tracker = LangChainTracker(
            agent_name="test_agent",
            session_id="test_session",
            config=mock_config
        )
        
        assert tracker.agent_name == "test_agent"
        assert tracker.session_id == "test_session"
        assert tracker.run_env == "local"
        assert tracker.emitter is not None
    
    def test_tracker_auto_session_id(self, mock_config):
        """Test automatic session ID generation."""
        tracker = LangChainTracker(
            agent_name="test_agent",
            config=mock_config
        )
        
        assert tracker.session_id is not None
        assert len(tracker.session_id) > 0
    
    def test_on_llm_start(self, mock_config):
        """Test LLM start callback."""
        tracker = LangChainTracker("test_agent", config=mock_config)
        tracker.emitter.emit_agent_event = MagicMock()
        
        run_id = uuid.uuid4()
        serialized = {"name": "OpenAI", "model_name": "gpt-4o"}
        
        tracker.on_llm_start(
            serialized=serialized,
            prompts=["test prompt"],
            run_id=run_id
        )
        
        # Verify event emission
        tracker.emitter.emit_agent_event.assert_called_once()
        call_args = tracker.emitter.emit_agent_event.call_args[1]
        
        assert call_args["agent_name"] == "test_agent"
        assert call_args["agent_framework"] == "langchain"
        assert call_args["event_type"] == "start"
        assert call_args["model"] == "gpt-4o"
        assert call_args["success"] is True
    
    def test_on_llm_end(self, mock_config):
        """Test LLM end callback."""
        tracker = LangChainTracker("test_agent", config=mock_config)
        tracker.emitter.emit_agent_event = MagicMock()
        
        run_id = uuid.uuid4()
        run_id_str = str(run_id)
        
        # Simulate start to set up tracking
        tracker._run_start_times[run_id_str] = 1000.0
        tracker._tool_calls[run_id_str] = []
        tracker._memory_events[run_id_str] = []
        
        # Mock LLMResult
        mock_response = MagicMock()
        mock_response.llm_output = {"model_name": "gpt-4o"}
        
        with patch('time.time', return_value=1001.0):  # 1 second later
            tracker.on_llm_end(response=mock_response, run_id=run_id)
        
        # Verify event emission
        tracker.emitter.emit_agent_event.assert_called_once()
        call_args = tracker.emitter.emit_agent_event.call_args[1]
        
        assert call_args["event_type"] == "end"
        assert call_args["duration_ms"] == 1000  # 1 second
        assert call_args["success"] is True
        
        # Verify cleanup
        assert run_id_str not in tracker._run_start_times
    
    def test_on_llm_error(self, mock_config):
        """Test LLM error callback."""
        tracker = LangChainTracker("test_agent", config=mock_config)
        tracker.emitter.emit_agent_event = MagicMock()
        
        run_id = uuid.uuid4()
        run_id_str = str(run_id)
        
        # Simulate start to set up tracking
        tracker._run_start_times[run_id_str] = 1000.0
        tracker._tool_calls[run_id_str] = []
        tracker._memory_events[run_id_str] = []
        
        error = ValueError("Test error")
        
        with patch('time.time', return_value=1000.5):  # 0.5 seconds later
            tracker.on_llm_error(error=error, run_id=run_id)
        
        # Verify event emission
        tracker.emitter.emit_agent_event.assert_called_once()
        call_args = tracker.emitter.emit_agent_event.call_args[1]
        
        assert call_args["event_type"] == "error"
        assert call_args["duration_ms"] == 500  # 0.5 seconds
        assert call_args["success"] is False
        assert call_args["exception"] == "ValueError"
    
    def test_on_tool_start(self, mock_config):
        """Test tool start callback."""
        tracker = LangChainTracker("test_agent", config=mock_config)
        
        run_id = uuid.uuid4()
        parent_run_id = uuid.uuid4()
        parent_run_id_str = str(parent_run_id)
        
        # Set up tracking for parent run
        tracker._tool_calls[parent_run_id_str] = []
        
        serialized = {"name": "search_tool"}
        
        tracker.on_tool_start(
            serialized=serialized,
            input_str="test input",
            run_id=run_id,
            parent_run_id=parent_run_id
        )
        
        # Verify tool call was added
        assert len(tracker._tool_calls[parent_run_id_str]) == 1
        tool_call = tracker._tool_calls[parent_run_id_str][0]
        assert tool_call.tool_name == "search_tool"
    
    def test_model_name_extraction(self, mock_config):
        """Test model name extraction from serialized data."""
        tracker = LangChainTracker("test_agent", config=mock_config)
        
        # Test direct model_name field
        serialized1 = {"model_name": "gpt-4o"}
        assert tracker._extract_model_name(serialized1) == "gpt-4o"
        
        # Test model field
        serialized2 = {"model": "claude-3"}
        assert tracker._extract_model_name(serialized2) == "claude-3"
        
        # Test nested in kwargs
        serialized3 = {"kwargs": {"model_name": "gpt-3.5"}}
        assert tracker._extract_model_name(serialized3) == "gpt-3.5"
        
        # Test unknown
        serialized4 = {"other_field": "value"}
        assert tracker._extract_model_name(serialized4) == "unknown"
    
    @pytest.mark.asyncio
    async def test_flush_events(self, mock_config):
        """Test manual event flushing."""
        tracker = LangChainTracker("test_agent", config=mock_config)
        tracker.emitter.flush_events = AsyncMock(return_value=True)
        
        result = await tracker.flush_events()
        
        assert result is True
        tracker.emitter.flush_events.assert_called_once()
    
    def test_get_buffer_size(self, mock_config):
        """Test getting buffer size."""
        tracker = LangChainTracker("test_agent", config=mock_config)
        tracker.emitter.get_buffer_size = MagicMock(return_value=3)
        
        size = tracker.get_buffer_size()
        
        assert size == 3
        tracker.emitter.get_buffer_size.assert_called_once()