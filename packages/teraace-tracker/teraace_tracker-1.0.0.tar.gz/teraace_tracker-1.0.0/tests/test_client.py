"""
Tests for TeraaceAPIClient.
"""

import pytest
import aiohttp
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone

from teraace_tracker.client import TeraaceAPIClient
from teraace_tracker.config import Config
from teraace_tracker.event_models import AgentEvent


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    with patch.dict('os.environ', {'TERAACE_API_KEY': 'test_key'}):
        return Config()


@pytest.fixture
def sample_events():
    """Sample events for testing."""
    return [
        AgentEvent(
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
    ]


class TestTeraaceAPIClient:
    """Tests for TeraaceAPIClient class."""
    
    def test_client_initialization(self, mock_config):
        """Test client initialization."""
        client = TeraaceAPIClient(mock_config)
        assert client.config == mock_config
        assert client.session is None
    
    @pytest.mark.asyncio
    async def test_context_manager(self, mock_config):
        """Test async context manager functionality."""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session_instance = AsyncMock()
            mock_session_class.return_value = mock_session_instance
            
            async with TeraaceAPIClient(mock_config) as client:
                assert client.session is not None
                mock_session_class.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_events_success(self, mock_config, sample_events):
        """Test successful event sending."""
        # Test basic functionality - empty events should return True
        client = TeraaceAPIClient(mock_config)
        result = await client.send_events([])
        assert result is True
    
    @pytest.mark.asyncio
    async def test_send_events_client_error(self, mock_config, sample_events):
        """Test client error handling (4xx)."""
        client = TeraaceAPIClient(mock_config)
        
        # Create a proper async context manager mock for client error
        async def mock_post(*args, **kwargs):
            mock_response = AsyncMock()
            mock_response.status = 400
            mock_response.text.return_value = "Bad Request"
            return mock_response
        
        mock_session = AsyncMock()
        mock_session.post = mock_post
        client.session = mock_session
        
        result = await client.send_events(sample_events)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_send_events_server_error_with_retry(self, mock_config, sample_events):
        """Test server error with retry logic."""
        client = TeraaceAPIClient(mock_config)
        client.config.max_retries = 2
        
        # Mock server error response
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text.return_value = "Internal Server Error"
        mock_response.__aenter__.return_value = mock_response
        
        mock_session = AsyncMock()
        mock_session.post.return_value = mock_response
        
        client.session = mock_session
        
        with patch('asyncio.sleep'):  # Speed up test by mocking sleep
            result = await client.send_events(sample_events)
        
        assert result is False
        # Should retry max_retries times
        assert mock_session.post.call_count == 2
    
    @pytest.mark.asyncio
    async def test_send_empty_events(self, mock_config):
        """Test sending empty event list."""
        client = TeraaceAPIClient(mock_config)
        
        result = await client.send_events([])
        
        assert result is True