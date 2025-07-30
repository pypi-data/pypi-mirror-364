"""
Tests for Pydantic event models.
"""

import pytest
from datetime import datetime, timezone
from teraace_tracker.event_models import ToolCall, MemoryEvent, AgentEvent


class TestToolCall:
    """Tests for ToolCall model."""
    
    def test_tool_call_creation(self):
        """Test creating a ToolCall."""
        timestamp = datetime.now(timezone.utc)
        tool_call = ToolCall(tool_name="search", timestamp=timestamp)
        
        assert tool_call.tool_name == "search"
        assert tool_call.timestamp == timestamp
    
    def test_tool_call_validation(self):
        """Test ToolCall validation."""
        # Test that empty tool name is allowed (Pydantic doesn't validate empty strings by default)
        tool_call = ToolCall(tool_name="", timestamp=datetime.now(timezone.utc))
        assert tool_call.tool_name == ""


class TestMemoryEvent:
    """Tests for MemoryEvent model."""
    
    def test_memory_event_creation(self):
        """Test creating a MemoryEvent."""
        timestamp = datetime.now(timezone.utc)
        memory_event = MemoryEvent(
            event_type="read",
            key="user_context",
            timestamp=timestamp
        )
        
        assert memory_event.event_type == "read"
        assert memory_event.key == "user_context"
        assert memory_event.timestamp == timestamp
    
    def test_memory_event_types(self):
        """Test different memory event types."""
        timestamp = datetime.now(timezone.utc)
        
        for event_type in ["read", "write", "update"]:
            memory_event = MemoryEvent(
                event_type=event_type,
                key="test_key",
                timestamp=timestamp
            )
            assert memory_event.event_type == event_type


class TestAgentEvent:
    """Tests for AgentEvent model."""
    
    def test_agent_event_creation(self):
        """Test creating an AgentEvent."""
        timestamp = datetime.now(timezone.utc)
        agent_event = AgentEvent(
            agent_name="test_agent",
            session_id="session_123",
            agent_framework="langchain",
            model="gpt-4o",
            runtime="python3.10/ubuntu",
            run_env="local",
            event_type="start",
            timestamp=timestamp,
            duration_ms=1000,
            success=True
        )
        
        assert agent_event.agent_name == "test_agent"
        assert agent_event.session_id == "session_123"
        assert agent_event.agent_framework == "langchain"
        assert agent_event.model == "gpt-4o"
        assert agent_event.runtime == "python3.10/ubuntu"
        assert agent_event.run_env == "local"
        assert agent_event.event_type == "start"
        assert agent_event.timestamp == timestamp
        assert agent_event.duration_ms == 1000
        assert agent_event.success is True
        assert agent_event.exception == ""
        assert agent_event.tool_calls == []
        assert agent_event.memory_events == []
        assert agent_event.event_id is not None
    
    def test_agent_event_with_tools_and_memory(self):
        """Test AgentEvent with tool calls and memory events."""
        timestamp = datetime.now(timezone.utc)
        tool_call = ToolCall(tool_name="search", timestamp=timestamp)
        memory_event = MemoryEvent(
            event_type="read",
            key="context",
            timestamp=timestamp
        )
        
        agent_event = AgentEvent(
            agent_name="test_agent",
            session_id="session_123",
            agent_framework="langchain",
            model="gpt-4o",
            runtime="python3.10/ubuntu",
            run_env="local",
            event_type="end",
            timestamp=timestamp,
            duration_ms=2000,
            success=True,
            tool_calls=[tool_call],
            memory_events=[memory_event]
        )
        
        assert len(agent_event.tool_calls) == 1
        assert len(agent_event.memory_events) == 1
        assert agent_event.tool_calls[0].tool_name == "search"
        assert agent_event.memory_events[0].event_type == "read"
    
    def test_agent_event_error(self):
        """Test AgentEvent for error case."""
        timestamp = datetime.now(timezone.utc)
        agent_event = AgentEvent(
            agent_name="test_agent",
            session_id="session_123",
            agent_framework="langchain",
            model="gpt-4o",
            runtime="python3.10/ubuntu",
            run_env="local",
            event_type="error",
            timestamp=timestamp,
            duration_ms=500,
            success=False,
            exception="ValueError"
        )
        
        assert agent_event.event_type == "error"
        assert agent_event.success is False
        assert agent_event.exception == "ValueError"