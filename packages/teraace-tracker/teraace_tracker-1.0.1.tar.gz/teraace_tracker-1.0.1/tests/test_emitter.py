"""
Tests for EventEmitter.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone

from teraace_tracker.emitter import EventEmitter
from teraace_tracker.config import Config
from teraace_tracker.event_models import ToolCall, MemoryEvent


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    with patch.dict('os.environ', {'TERAACE_API_KEY': 'test_key'}):
        return Config()


class TestEventEmitter:
    """Tests for EventEmitter class."""
    
    def test_emitter_initialization(self, mock_config):
        """Test emitter initialization."""
        emitter = EventEmitter(mock_config)
        assert emitter.config == mock_config
        assert emitter.buffer is not None
        assert "python" in emitter._runtime
    
    def test_emit_agent_event(self, mock_config):
        """Test emitting agent events."""
        emitter = EventEmitter(mock_config)
        
        # Mock the buffer to verify event is added
        emitter.buffer.add_event = MagicMock()
        
        emitter.emit_agent_event(
            agent_name="test_agent",
            session_id="test_session",
            agent_framework="langchain",
            model="gpt-4o",
            event_type="start",
            duration_ms=100
        )
        
        emitter.buffer.add_event.assert_called_once()
        
        # Verify the event has correct properties
        event = emitter.buffer.add_event.call_args[0][0]
        assert event.agent_name == "test_agent"
        assert event.session_id == "test_session"
        assert event.agent_framework == "langchain"
        assert event.model == "gpt-4o"
        assert event.event_type == "start"
        assert event.duration_ms == 100
        assert event.success is True
        assert event.exception == ""
        assert event.run_env == "local"
        assert "python" in event.runtime
    
    def test_emit_agent_event_with_tools_and_memory(self, mock_config):
        """Test emitting agent event with tool calls and memory events."""
        emitter = EventEmitter(mock_config)
        emitter.buffer.add_event = MagicMock()
        
        tool_call = ToolCall(tool_name="search", timestamp=datetime.now(timezone.utc))
        memory_event = MemoryEvent(
            event_type="read",
            key="context",
            timestamp=datetime.now(timezone.utc)
        )
        
        emitter.emit_agent_event(
            agent_name="test_agent",
            session_id="test_session",
            agent_framework="langchain",
            model="gpt-4o",
            event_type="end",
            duration_ms=2000,
            success=True,
            tool_calls=[tool_call],
            memory_events=[memory_event]
        )
        
        event = emitter.buffer.add_event.call_args[0][0]
        assert len(event.tool_calls) == 1
        assert len(event.memory_events) == 1
        assert event.tool_calls[0].tool_name == "search"
        assert event.memory_events[0].event_type == "read"
    
    def test_emit_error_event(self, mock_config):
        """Test emitting error events."""
        emitter = EventEmitter(mock_config)
        emitter.buffer.add_event = MagicMock()
        
        emitter.emit_agent_event(
            agent_name="test_agent",
            session_id="test_session",
            agent_framework="langchain",
            model="gpt-4o",
            event_type="error",
            duration_ms=500,
            success=False,
            exception="ValueError"
        )
        
        event = emitter.buffer.add_event.call_args[0][0]
        assert event.event_type == "error"
        assert event.success is False
        assert event.exception == "ValueError"
    
    def test_create_tool_call(self, mock_config):
        """Test creating tool call objects."""
        emitter = EventEmitter(mock_config)
        
        tool_call = emitter.create_tool_call("search_tool")
        
        assert isinstance(tool_call, ToolCall)
        assert tool_call.tool_name == "search_tool"
        assert isinstance(tool_call.timestamp, datetime)
    
    def test_create_memory_event(self, mock_config):
        """Test creating memory event objects."""
        emitter = EventEmitter(mock_config)
        
        memory_event = emitter.create_memory_event("write", "user_data")
        
        assert isinstance(memory_event, MemoryEvent)
        assert memory_event.event_type == "write"
        assert memory_event.key == "user_data"
        assert isinstance(memory_event.timestamp, datetime)
    
    @pytest.mark.asyncio
    async def test_flush_events(self, mock_config):
        """Test manual event flushing."""
        emitter = EventEmitter(mock_config)
        
        # Mock the buffer flush method
        emitter.buffer.flush = AsyncMock(return_value=True)
        
        result = await emitter.flush_events()
        
        assert result is True
        emitter.buffer.flush.assert_called_once()
    
    def test_get_buffer_size(self, mock_config):
        """Test getting buffer size."""
        emitter = EventEmitter(mock_config)
        
        # Mock buffer size
        emitter.buffer.get_buffer_size = MagicMock(return_value=5)
        
        size = emitter.get_buffer_size()
        
        assert size == 5
        emitter.buffer.get_buffer_size.assert_called_once()