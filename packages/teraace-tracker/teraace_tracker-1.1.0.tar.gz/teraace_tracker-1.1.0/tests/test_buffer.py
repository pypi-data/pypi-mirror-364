"""
Tests for EventBuffer.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone

from teraace_tracker.buffer import EventBuffer
from teraace_tracker.config import Config
from teraace_tracker.event_models import AgentEvent


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    with patch.dict('os.environ', {'TERAACE_API_KEY': 'test_key'}):
        config = Config()
        config.buffer_size = 3  # Small buffer for testing
        return config


@pytest.fixture
def sample_event():
    """Sample AgentEvent for testing."""
    return AgentEvent(
        agent_name="test_agent",
        session_id="test_session",
        agent_framework="langchain",
        model="gpt-4o",
        runtime="python3.10/ubuntu",
        run_env="local",
        event_type="start",
        timestamp=datetime.now(timezone.utc),
        duration_ms=100,
        success=True
    )


class TestEventBuffer:
    """Tests for EventBuffer class."""
    
    def test_buffer_initialization(self, mock_config):
        """Test buffer initialization."""
        buffer = EventBuffer(mock_config)
        assert buffer.get_buffer_size() == 0
        assert buffer.config == mock_config
    
    def test_add_event(self, mock_config, sample_event):
        """Test adding events to buffer."""
        buffer = EventBuffer(mock_config)
        
        buffer.add_event(sample_event)
        assert buffer.get_buffer_size() == 1
        
        # Add more events
        for i in range(2):
            buffer.add_event(sample_event)
        
        assert buffer.get_buffer_size() == 3
    
    @pytest.mark.asyncio
    async def test_manual_flush(self, mock_config, sample_event):
        """Test manual flush functionality."""
        buffer = EventBuffer(mock_config)
        
        # Add events
        buffer.add_event(sample_event)
        buffer.add_event(sample_event)
        
        # Mock the API client
        with patch('teraace_tracker.buffer.TeraaceAPIClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.send_events.return_value = True
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            success = await buffer.flush()
            
            assert success is True
            assert buffer.get_buffer_size() == 0  # Buffer should be empty after flush
            mock_instance.send_events.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_flush_failure_restores_events(self, mock_config, sample_event):
        """Test that failed flush restores events to buffer."""
        buffer = EventBuffer(mock_config)
        buffer.add_event(sample_event)
        
        # Mock failed API call
        with patch('teraace_tracker.buffer.TeraaceAPIClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.send_events.return_value = False
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            success = await buffer.flush()
            
            assert success is False
            assert buffer.get_buffer_size() == 1  # Event should be restored
    
    def test_clear_buffer(self, mock_config, sample_event):
        """Test buffer clearing."""
        buffer = EventBuffer(mock_config)
        
        buffer.add_event(sample_event)
        buffer.add_event(sample_event)
        assert buffer.get_buffer_size() == 2
        
        buffer.clear_buffer()
        assert buffer.get_buffer_size() == 0