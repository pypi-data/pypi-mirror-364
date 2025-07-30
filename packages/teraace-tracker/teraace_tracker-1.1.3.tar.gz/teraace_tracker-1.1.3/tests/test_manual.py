"""
Tests for manual event emission and custom functionality.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from teraace_tracker.emitter import EventEmitter
from teraace_tracker.config import Config
from teraace_tracker.event_models import ToolCall, MemoryEvent


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    with patch.dict('os.environ', {'TERAACE_API_KEY': 'test_key'}):
        return Config()


class TestManualEventEmission:
    """Tests for manual event emission functionality."""
    
    def test_custom_config_with_direct_arguments(self):
        """Test configuration with direct arguments."""
        with patch.dict('os.environ', {'TERAACE_API_KEY': 'test_key'}):
            config = Config(
                buffer_size=15,
                api_endpoint="https://custom-api.example.com/events",
                request_timeout=45,
                max_retries=5
            )
            
            assert config.buffer_size == 15
            assert config.api_endpoint == "https://custom-api.example.com/events"
            assert config.request_timeout == 45
            assert config.max_retries == 5
    
    def test_custom_config_precedence(self):
        """Test that direct arguments take precedence over environment variables."""
        with patch.dict('os.environ', {
            'TERAACE_API_KEY': 'test_key',
            'TERAACE_BUFFER_SIZE': '10',
            'TERAACE_API_ENDPOINT': 'https://env-api.example.com',
            'TERAACE_REQUEST_TIMEOUT': '20',
            'TERAACE_MAX_RETRIES': '2'
        }):
            config = Config(
                buffer_size=25,
                api_endpoint="https://direct-api.example.com",
                request_timeout=60,
                max_retries=7
            )
            
            # Direct arguments should override environment variables
            assert config.buffer_size == 25
            assert config.api_endpoint == "https://direct-api.example.com"
            assert config.request_timeout == 60
            assert config.max_retries == 7
    
    def test_emit_custom_event(self, mock_config):
        """Test emitting custom events with additional metadata."""
        emitter = EventEmitter(mock_config)
        emitter.emit_agent_event = MagicMock()
        
        emitter.emit_custom_event(
            agent_name="custom_agent",
            session_id="custom_session",
            agent_framework="custom_framework",
            model="custom-model",
            event_type="custom_operation",
            duration_ms=1500,
            success=True,
            run_env="edge",
            custom_field1="value1",
            custom_field2=42,
            custom_metadata={"nested": "data"}
        )
        
        # Should call the underlying emit_agent_event method
        emitter.emit_agent_event.assert_called_once()
        call_args = emitter.emit_agent_event.call_args[1]
        
        assert call_args["agent_name"] == "custom_agent"
        assert call_args["session_id"] == "custom_session"
        assert call_args["agent_framework"] == "custom_framework"
        assert call_args["model"] == "custom-model"
        assert call_args["event_type"] == "custom_operation"
        assert call_args["duration_ms"] == 1500
        assert call_args["success"] is True
        assert call_args["run_env"] == "edge"
    
    def test_buffer_overflow_handling(self, mock_config):
        """Test buffer overflow handling."""
        # Set a small buffer size for testing
        mock_config.buffer_size = 3
        emitter = EventEmitter(mock_config)
        
        # Fill buffer beyond capacity
        for i in range(10):
            emitter.emit_agent_event(
                agent_name=f"agent_{i}",
                session_id="test_session",
                agent_framework="test",
                model="test-model",
                event_type="start",
                duration_ms=100,
                success=True
            )
        
        # Buffer should not exceed double the configured size
        buffer_size = emitter.get_buffer_size()
        assert buffer_size <= mock_config.buffer_size * 2
    
    def test_manual_event_with_all_fields(self, mock_config):
        """Test manual event emission with all possible fields."""
        emitter = EventEmitter(mock_config)
        emitter.buffer.add_event = MagicMock()
        
        tool_calls = [
            ToolCall(tool_name="tool1", timestamp=datetime.now(timezone.utc)),
            ToolCall(tool_name="tool2", timestamp=datetime.now(timezone.utc))
        ]
        
        memory_events = [
            MemoryEvent(event_type="read", key="key1", timestamp=datetime.now(timezone.utc)),
            MemoryEvent(event_type="write", key="key2", timestamp=datetime.now(timezone.utc))
        ]
        
        emitter.emit_agent_event(
            agent_name="comprehensive_agent",
            session_id="comprehensive_session",
            agent_framework="comprehensive_framework",
            model="comprehensive-model",
            event_type="comprehensive_operation",
            duration_ms=2500,
            success=True,
            exception="",
            tool_calls=tool_calls,
            memory_events=memory_events,
            run_env="comprehensive_env"
        )
        
        # Verify event was added to buffer
        emitter.buffer.add_event.assert_called_once()
        event = emitter.buffer.add_event.call_args[0][0]
        
        assert event.agent_name == "comprehensive_agent"
        assert event.session_id == "comprehensive_session"
        assert event.agent_framework == "comprehensive_framework"
        assert event.model == "comprehensive-model"
        assert event.event_type == "comprehensive_operation"
        assert event.duration_ms == 2500
        assert event.success is True
        assert event.exception == ""
        assert len(event.tool_calls) == 2
        assert len(event.memory_events) == 2
        assert event.run_env == "comprehensive_env"


class TestHighThroughputScenarios:
    """Tests for high-throughput agent activity scenarios."""
    
    def test_rapid_event_emission(self, mock_config):
        """Test rapid emission of many events."""
        # Use a larger buffer for this test
        mock_config.buffer_size = 50
        emitter = EventEmitter(mock_config)
        emitter.buffer._flush_async = MagicMock()
        
        # Emit many events rapidly
        event_count = 100
        for i in range(event_count):
            emitter.emit_agent_event(
                agent_name=f"rapid_agent_{i % 10}",  # 10 different agents
                session_id=f"session_{i % 5}",       # 5 different sessions
                agent_framework="high_throughput",
                model=f"model_{i % 3}",               # 3 different models
                event_type="rapid_operation",
                duration_ms=i * 10,
                success=True,
                run_env="performance_test"
            )
        
        # Buffer should handle the load appropriately
        buffer_size = emitter.get_buffer_size()
        assert buffer_size <= mock_config.buffer_size * 2  # Should not exceed overflow limit
    
    def test_concurrent_agent_simulation(self, mock_config):
        """Test simulation of multiple concurrent agents."""
        mock_config.buffer_size = 30
        emitter = EventEmitter(mock_config)
        emitter.buffer._flush_async = MagicMock()
        
        # Simulate 5 concurrent agents each doing 20 operations
        agents = ["agent_A", "agent_B", "agent_C", "agent_D", "agent_E"]
        models = ["gpt-4o", "claude-3", "gpt-3.5-turbo"]
        
        for agent in agents:
            session_id = f"{agent}_session"
            for operation in range(20):
                # Start event
                emitter.emit_agent_event(
                    agent_name=agent,
                    session_id=session_id,
                    agent_framework="concurrent_test",
                    model=models[operation % len(models)],
                    event_type="start",
                    duration_ms=0,
                    success=True,
                    run_env="concurrent"
                )
                
                # End event
                emitter.emit_agent_event(
                    agent_name=agent,
                    session_id=session_id,
                    agent_framework="concurrent_test",
                    model=models[operation % len(models)],
                    event_type="end",
                    duration_ms=operation * 100,
                    success=True,
                    tool_calls=[
                        emitter.create_tool_call(f"tool_{operation % 3}")
                    ],
                    memory_events=[
                        emitter.create_memory_event("read", f"key_{operation}")
                    ],
                    run_env="concurrent"
                )
        
        # Should have processed all events without issues
        final_buffer_size = emitter.get_buffer_size()
        assert final_buffer_size >= 0  # Buffer should be in valid state
    
    def test_mixed_event_types_high_volume(self, mock_config):
        """Test high volume of mixed event types."""
        mock_config.buffer_size = 25
        emitter = EventEmitter(mock_config)
        emitter.buffer._flush_async = MagicMock()
        
        event_types = ["start", "end", "error"]
        frameworks = ["langchain", "crewai", "autogpt", "custom"]
        
        # Generate 200 mixed events
        for i in range(200):
            event_type = event_types[i % len(event_types)]
            framework = frameworks[i % len(frameworks)]
            
            success = event_type != "error"
            exception = "TestException" if event_type == "error" else ""
            
            emitter.emit_agent_event(
                agent_name=f"mixed_agent_{i % 20}",
                session_id=f"mixed_session_{i % 10}",
                agent_framework=framework,
                model=f"model_{i % 4}",
                event_type=event_type,
                duration_ms=i * 5,
                success=success,
                exception=exception,
                run_env="mixed_test"
            )
        
        # System should handle mixed load gracefully
        assert emitter.get_buffer_size() >= 0
        
        # Should have triggered multiple flush attempts due to volume
        assert emitter.buffer._flush_async.call_count > 0