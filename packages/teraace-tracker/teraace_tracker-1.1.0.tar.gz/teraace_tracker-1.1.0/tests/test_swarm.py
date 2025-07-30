"""Tests for Swarm integration."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from teraace_tracker.integrations.swarm import SwarmTracker


class TestSwarmTracker:
    """Test cases for SwarmTracker."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = SwarmTracker()

    def test_initialization(self):
        """Test tracker initialization."""
        assert self.tracker.framework_name == "swarm"
        assert hasattr(self.tracker, 'emitter')
        assert hasattr(self.tracker, '_tracked_agents')
        assert hasattr(self.tracker, '_active_conversations')

    def test_track_agent_creation(self):
        """Test agent creation tracking."""
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.__class__.__name__ = "Agent"
        mock_agent.model = "gpt-4"
        mock_agent.instructions = "You are a helpful assistant"
        mock_agent.functions = []
        mock_agent.tool_choice = "auto"
        mock_agent.parallel_tool_calls = True
        
        agent_config = {
            "model": "gpt-4",
            "instructions": "You are a helpful assistant"
        }
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_agent_creation(mock_agent, agent_config)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'agent_creation'
            assert call_args['data']['agent_name'] == 'TestAgent'
            assert call_args['data']['model'] == 'gpt-4'

    def test_track_swarm_run(self):
        """Test Swarm run tracking."""
        mock_client = Mock()
        mock_agent = Mock()
        mock_agent.name = "StartAgent"
        mock_agent.__class__.__name__ = "Agent"
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_swarm_run(
                client=mock_client,
                agent=mock_agent,
                messages=messages,
                context_variables={"user_id": "123"},
                max_turns=10
            )
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'swarm_run_start'
            assert call_args['data']['starting_agent'] == 'StartAgent'
            assert call_args['data']['message_count'] == 1

    def test_track_agent_handoff(self):
        """Test agent handoff tracking."""
        mock_from_agent = Mock()
        mock_from_agent.name = "Agent1"
        mock_from_agent.__class__.__name__ = "SalesAgent"
        
        mock_to_agent = Mock()
        mock_to_agent.name = "Agent2"
        mock_to_agent.__class__.__name__ = "SupportAgent"
        
        context = {"user_id": "123", "issue": "billing"}
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_agent_handoff(mock_from_agent, mock_to_agent, context)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'agent_handoff'
            assert call_args['data']['from_agent'] == 'Agent1'
            assert call_args['data']['to_agent'] == 'Agent2'

    def test_track_function_execution(self):
        """Test function execution tracking."""
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        
        mock_function = Mock()
        mock_function.__name__ = "get_weather"
        mock_function.__module__ = "weather_tools"
        
        arguments = {"location": "New York"}
        result = {"temperature": "72F", "condition": "sunny"}
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_function_execution(mock_agent, mock_function, arguments, result)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'function_execution'
            assert call_args['data']['function_name'] == 'get_weather'
            assert call_args['data']['arguments'] == arguments

    def test_track_context_update(self):
        """Test context update tracking."""
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        
        old_context = {"user_id": "123"}
        new_context = {"user_id": "123", "session_id": "abc", "preferences": "dark_mode"}
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_context_update(mock_agent, old_context, new_context)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'context_update'
            assert 'session_id' in call_args['data']['added_keys']
            assert 'preferences' in call_args['data']['added_keys']

    def test_track_response_generation(self):
        """Test response generation tracking."""
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        
        messages = [{"role": "user", "content": "Hello"}]
        response = {
            "content": "Hello! How can I help you?",
            "role": "assistant",
            "tool_calls": [],
            "finish_reason": "stop",
            "usage": {"prompt_tokens": 10, "completion_tokens": 8}
        }
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_response_generation(mock_agent, messages, response)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'response_generation'
            assert call_args['data']['response_content'] == "Hello! How can I help you?"

    def test_track_swarm_completion(self):
        """Test Swarm completion tracking."""
        mock_agent = Mock()
        mock_agent.name = "FinalAgent"
        mock_agent.__class__.__name__ = "Agent"
        
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "Thanks"}
        ]
        context = {"resolved": True, "satisfaction": "high"}
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_swarm_completion(mock_agent, messages, context)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'swarm_completion'
            assert call_args['data']['final_agent'] == 'FinalAgent'
            assert call_args['data']['total_messages'] == 3
            assert call_args['data']['conversation_turns'] == 2

    def test_auto_track_agents(self):
        """Test automatic agent tracking."""
        mock_agent1 = Mock()
        mock_agent1.name = "Agent1"
        mock_agent1.model = "gpt-4"
        mock_agent1.instructions = "Assistant 1"
        mock_agent1.functions = []
        
        mock_agent2 = Mock()
        mock_agent2.name = "Agent2"
        mock_agent2.model = "gpt-3.5-turbo"
        mock_agent2.instructions = "Assistant 2"
        mock_agent2.functions = []
        
        with patch.object(self.tracker, 'track_agent_creation') as mock_track:
            result = self.tracker.auto_track_agents(mock_agent1, mock_agent2)
            
            # Verify both agents were tracked
            assert mock_track.call_count == 2
            assert result == (mock_agent1, mock_agent2)
            
            # Verify agents were stored
            assert len(self.tracker._tracked_agents) == 2

    def test_auto_track_single_agent(self):
        """Test automatic tracking of single agent."""
        mock_agent = Mock()
        mock_agent.name = "SingleAgent"
        mock_agent.model = "gpt-4"
        mock_agent.instructions = "Single assistant"
        mock_agent.functions = []
        
        with patch.object(self.tracker, 'track_agent_creation') as mock_track:
            result = self.tracker.auto_track_agents(mock_agent)
            
            # Verify agent was tracked
            mock_track.assert_called_once()
            assert result == mock_agent