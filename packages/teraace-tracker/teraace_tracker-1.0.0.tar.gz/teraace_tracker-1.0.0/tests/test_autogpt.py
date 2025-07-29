"""
Tests for AutoGPT integration.
"""

import pytest
import time
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

from teraace_tracker.integrations.autogpt import AutoGPTTracker, CommandExecutionContext
from teraace_tracker.config import Config


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    with patch.dict('os.environ', {'TERAACE_API_KEY': 'test_key'}):
        return Config()


class MockAutoGPTAgent:
    """Mock AutoGPT agent for testing."""
    
    def __init__(self, name: str, model: str = "gpt-4o"):
        self.name = name
        self.model = model
        self.config = MagicMock()
        self.config.model = model
        self.llm = MagicMock()
        self.llm.model_name = model
    
    def run(self, goal: str):
        """Mock run method."""
        time.sleep(0.1)
        return f"Goal achieved: {goal}"
    
    def execute_command(self, command: str, args: str = ""):
        """Mock execute command method."""
        return f"Executed {command}"
    
    def think(self):
        """Mock think method."""
        return "Thinking completed"


class TestAutoGPTTracker:
    """Tests for AutoGPTTracker class."""
    
    def test_tracker_initialization(self, mock_config):
        """Test tracker initialization."""
        tracker = AutoGPTTracker(
            agent_name="test_autogpt_agent",
            session_id="test_session",
            config=mock_config
        )
        
        assert tracker.agent_name == "test_autogpt_agent"
        assert tracker.session_id == "test_session"
        assert tracker.run_env == "local"
        assert tracker.emitter is not None
    
    def test_tracker_auto_session_id(self, mock_config):
        """Test automatic session ID generation."""
        tracker = AutoGPTTracker(
            agent_name="test_autogpt_agent",
            config=mock_config
        )
        
        assert tracker.session_id is not None
        assert len(tracker.session_id) > 0
    
    def test_patch_agent_loop(self, mock_config):
        """Test patching AutoGPT agent loop."""
        tracker = AutoGPTTracker("test_agent", config=mock_config)
        agent = MockAutoGPTAgent("TestAgent")
        
        # Store original methods
        original_run = agent.run
        original_execute = agent.execute_command
        original_think = agent.think
        
        # Patch the agent
        patched_agent = tracker.patch_agent_loop(agent)
        
        # Verify methods were wrapped
        assert patched_agent.run != original_run
        assert patched_agent.execute_command != original_execute
        assert patched_agent.think != original_think
        
        # Verify it's the same agent instance
        assert patched_agent is agent
    
    def test_wrapped_run_method_success(self, mock_config):
        """Test wrapped run method for successful execution."""
        tracker = AutoGPTTracker("test_agent", config=mock_config)
        tracker.emitter.emit_agent_event = MagicMock()
        
        agent = MockAutoGPTAgent("TestAgent")
        patched_agent = tracker.patch_agent_loop(agent)
        
        result = patched_agent.run("test goal")
        
        assert result == "Goal achieved: test goal"
        
        # Should emit start and end events
        assert tracker.emitter.emit_agent_event.call_count == 2
        
        # Check start event
        start_call = tracker.emitter.emit_agent_event.call_args_list[0][1]
        assert start_call["agent_name"] == "test_agent"
        assert start_call["agent_framework"] == "autogpt"
        assert start_call["event_type"] == "start"
        assert start_call["success"] is True
        
        # Check end event
        end_call = tracker.emitter.emit_agent_event.call_args_list[1][1]
        assert end_call["event_type"] == "end"
        assert end_call["success"] is True
        assert end_call["duration_ms"] >= 100  # At least 100ms due to sleep
    
    def test_wrapped_run_method_error(self, mock_config):
        """Test wrapped run method for error case."""
        tracker = AutoGPTTracker("test_agent", config=mock_config)
        tracker.emitter.emit_agent_event = MagicMock()
        
        agent = MockAutoGPTAgent("TestAgent")
        
        # Make run method raise an exception
        def failing_run(goal):
            raise RuntimeError("Test error")
        
        agent.run = failing_run
        patched_agent = tracker.patch_agent_loop(agent)
        
        with pytest.raises(RuntimeError):
            patched_agent.run("test goal")
        
        # Should emit start and error events
        assert tracker.emitter.emit_agent_event.call_count == 2
        
        # Check error event
        error_call = tracker.emitter.emit_agent_event.call_args_list[1][1]
        assert error_call["event_type"] == "error"
        assert error_call["success"] is False
        assert error_call["exception"] == "RuntimeError"
    
    def test_wrapped_execute_command(self, mock_config):
        """Test wrapped execute_command method."""
        tracker = AutoGPTTracker("test_agent", config=mock_config)
        tracker.log_tool_call = MagicMock()
        
        agent = MockAutoGPTAgent("TestAgent")
        patched_agent = tracker.patch_agent_loop(agent)
        
        result = patched_agent.execute_command("test_command", "test_args")
        
        assert result == "Executed test_command"
        tracker.log_tool_call.assert_called_once_with("test_command")
    
    def test_wrapped_think_method(self, mock_config):
        """Test wrapped think method."""
        tracker = AutoGPTTracker("test_agent", config=mock_config)
        tracker.log_memory_event = MagicMock()
        
        agent = MockAutoGPTAgent("TestAgent")
        patched_agent = tracker.patch_agent_loop(agent)
        
        result = patched_agent.think()
        
        assert result == "Thinking completed"
        
        # Should log memory read and write events
        assert tracker.log_memory_event.call_count == 2
        tracker.log_memory_event.assert_any_call("read", "agent_context")
        tracker.log_memory_event.assert_any_call("write", "agent_thoughts")
    
    def test_command_execution_context_success(self, mock_config):
        """Test command execution context manager for successful execution."""
        tracker = AutoGPTTracker("test_agent", config=mock_config)
        tracker.emitter.emit_agent_event = MagicMock()
        
        with tracker.track_command_execution("test_command", "gpt-4o") as cmd_context:
            cmd_context.log_tool_call("test_tool")
            cmd_context.log_memory_event("read", "test_key")
            time.sleep(0.1)
        
        # Should emit start and end events
        assert tracker.emitter.emit_agent_event.call_count == 2
        
        # Check start event
        start_call = tracker.emitter.emit_agent_event.call_args_list[0][1]
        assert start_call["agent_name"] == "test_agent:test_command"
        assert start_call["event_type"] == "start"
        assert start_call["model"] == "gpt-4o"
        
        # Check end event
        end_call = tracker.emitter.emit_agent_event.call_args_list[1][1]
        assert end_call["event_type"] == "end"
        assert end_call["success"] is True
        assert len(end_call["tool_calls"]) == 1
        assert len(end_call["memory_events"]) == 1
    
    def test_command_execution_context_error(self, mock_config):
        """Test command execution context manager for error case."""
        tracker = AutoGPTTracker("test_agent", config=mock_config)
        tracker.emitter.emit_agent_event = MagicMock()
        
        with pytest.raises(ValueError):
            with tracker.track_command_execution("test_command", "gpt-4o"):
                raise ValueError("Test error")
        
        # Should emit start and error events
        assert tracker.emitter.emit_agent_event.call_count == 2
        
        # Check error event
        error_call = tracker.emitter.emit_agent_event.call_args_list[1][1]
        assert error_call["event_type"] == "error"
        assert error_call["success"] is False
        assert error_call["exception"] == "ValueError"
    
    def test_log_tool_call(self, mock_config):
        """Test logging tool calls."""
        tracker = AutoGPTTracker("test_agent", config=mock_config)
        tracker.emitter.create_tool_call = MagicMock()
        
        tracker.log_tool_call("test_tool")
        
        tracker.emitter.create_tool_call.assert_called_once_with("test_tool")
    
    def test_log_memory_event(self, mock_config):
        """Test logging memory events."""
        tracker = AutoGPTTracker("test_agent", config=mock_config)
        tracker.emitter.create_memory_event = MagicMock()
        
        tracker.log_memory_event("read", "test_key")
        
        tracker.emitter.create_memory_event.assert_called_once_with("read", "test_key")
    
    def test_extract_model_info(self, mock_config):
        """Test model information extraction."""
        tracker = AutoGPTTracker("test_agent", config=mock_config)
        
        # Test direct model attribute
        agent1 = MagicMock()
        agent1.model = "gpt-4o"
        model = tracker._extract_model_info(agent1)
        assert model == "gpt-4o"
        
        # Test unknown case - agent with no model attributes
        agent2 = type('MockAgent', (), {})()  # Empty object
        model = tracker._extract_model_info(agent2)
        assert model == "unknown"
    
    @pytest.mark.asyncio
    async def test_flush_events(self, mock_config):
        """Test manual event flushing."""
        tracker = AutoGPTTracker("test_agent", config=mock_config)
        tracker.emitter.flush_events = AsyncMock(return_value=True)
        
        result = await tracker.flush_events()
        
        assert result is True
        tracker.emitter.flush_events.assert_called_once()
    
    def test_get_buffer_size(self, mock_config):
        """Test getting buffer size."""
        tracker = AutoGPTTracker("test_agent", config=mock_config)
        tracker.emitter.get_buffer_size = MagicMock(return_value=3)
        
        size = tracker.get_buffer_size()
        
        assert size == 3
        tracker.emitter.get_buffer_size.assert_called_once()


class TestCommandExecutionContext:
    """Tests for CommandExecutionContext class."""
    
    def test_context_manager_lifecycle(self, mock_config):
        """Test context manager enter and exit lifecycle."""
        tracker = AutoGPTTracker("test_agent", config=mock_config)
        tracker.emitter.emit_agent_event = MagicMock()
        
        context = CommandExecutionContext(tracker, "test_command", "gpt-4o")
        
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
        tracker = AutoGPTTracker("test_agent", config=mock_config)
        tracker.emitter.emit_agent_event = MagicMock()
        
        context = CommandExecutionContext(tracker, "test_command", "gpt-4o")
        context.__enter__()
        
        # Test exit with exception
        context.__exit__(RuntimeError, RuntimeError("test"), None)
        
        # Should have emitted start and error events
        assert tracker.emitter.emit_agent_event.call_count == 2
        
        # Check error event
        error_call = tracker.emitter.emit_agent_event.call_args_list[1][1]
        assert error_call["event_type"] == "error"
        assert error_call["success"] is False
        assert error_call["exception"] == "RuntimeError"