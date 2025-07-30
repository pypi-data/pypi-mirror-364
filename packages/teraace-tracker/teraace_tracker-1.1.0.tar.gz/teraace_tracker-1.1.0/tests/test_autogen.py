"""Tests for AutoGen integration."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from teraace_tracker.integrations.autogen import AutoGenTracker


class TestAutoGenTracker:
    """Test cases for AutoGenTracker."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = AutoGenTracker()

    def test_initialization(self):
        """Test tracker initialization."""
        assert self.tracker.framework_name == "autogen"
        assert hasattr(self.tracker, 'emitter')
        assert hasattr(self.tracker, '_tracked_agents')
        assert hasattr(self.tracker, '_conversation_history')

    def test_track_agent_creation(self):
        """Test agent creation tracking."""
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.__class__.__name__ = "AssistantAgent"
        mock_agent.system_message = "You are a helpful assistant"
        mock_agent.human_input_mode = "NEVER"
        mock_agent.max_consecutive_auto_reply = 5
        
        agent_config = {
            "llm_config": {"model": "gpt-4", "temperature": 0.7},
            "system_message": "You are a helpful assistant"
        }
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_agent_creation(mock_agent, agent_config)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'agent_creation'
            assert call_args['data']['agent_name'] == 'TestAgent'
            assert call_args['data']['agent_type'] == 'AssistantAgent'

    def test_track_conversation_start(self):
        """Test conversation start tracking."""
        mock_initiator = Mock()
        mock_initiator.name = "UserProxy"
        mock_initiator.__class__.__name__ = "UserProxyAgent"
        
        mock_recipient = Mock()
        mock_recipient.name = "Assistant"
        mock_recipient.__class__.__name__ = "AssistantAgent"
        
        message = "Hello, can you help me with coding?"
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_conversation_start(
                initiator=mock_initiator,
                recipient=mock_recipient,
                message=message,
                max_turns=10,
                silent=False
            )
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'conversation_start'
            assert call_args['data']['initiator_name'] == 'UserProxy'
            assert call_args['data']['recipient_name'] == 'Assistant'
            assert call_args['data']['initial_message'] == message

    def test_track_message_exchange(self):
        """Test message exchange tracking."""
        mock_sender = Mock()
        mock_sender.name = "Agent1"
        mock_sender.__class__.__name__ = "AssistantAgent"
        
        mock_recipient = Mock()
        mock_recipient.name = "Agent2"
        mock_recipient.__class__.__name__ = "UserProxyAgent"
        
        message = {
            "content": "Here's the code you requested",
            "role": "assistant",
            "name": "Agent1"
        }
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_message_exchange(mock_sender, mock_recipient, message)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'message_exchange'
            assert call_args['data']['sender_name'] == 'Agent1'
            assert call_args['data']['recipient_name'] == 'Agent2'
            assert call_args['data']['content'] == "Here's the code you requested"
            
            # Verify message was added to history
            assert len(self.tracker._conversation_history) == 1

    def test_track_function_call(self):
        """Test function call tracking."""
        mock_agent = Mock()
        mock_agent.name = "CodeAgent"
        mock_agent.__class__.__name__ = "AssistantAgent"
        
        function_name = "execute_code"
        arguments = {"language": "python", "code": "print('hello')"}
        result = {"output": "hello", "status": "success"}
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_function_call(mock_agent, function_name, arguments, result)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'function_call'
            assert call_args['data']['agent_name'] == 'CodeAgent'
            assert call_args['data']['function_name'] == function_name
            assert call_args['data']['arguments'] == arguments

    def test_track_group_chat(self):
        """Test group chat tracking."""
        mock_agent1 = Mock()
        mock_agent1.name = "Agent1"
        mock_agent2 = Mock()
        mock_agent2.name = "Agent2"
        mock_agent3 = Mock()
        mock_agent3.name = "Agent3"
        
        mock_group_chat = Mock()
        mock_group_chat.agents = [mock_agent1, mock_agent2, mock_agent3]
        mock_group_chat.max_round = 15
        mock_group_chat.admin_name = None
        
        messages = [
            {"content": "Hello", "role": "user"},
            {"content": "Hi there", "role": "assistant"},
            {"content": "How can I help?", "role": "assistant"}
        ]
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_group_chat(mock_group_chat, messages)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'group_chat'
            assert call_args['data']['agent_count'] == 3
            assert 'Agent1' in call_args['data']['agent_names']
            assert call_args['data']['message_count'] == 3

    def test_track_conversation_end(self):
        """Test conversation end tracking."""
        # Add some messages to history first
        self.tracker._conversation_history = [
            {"sender_name": "Agent1", "content": "Hello"},
            {"sender_name": "Agent2", "content": "Hi"}
        ]
        
        summary = "Successfully completed the coding task"
        total_messages = 5
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_conversation_end(summary, total_messages)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'conversation_end'
            assert call_args['data']['summary'] == summary
            assert call_args['data']['total_messages'] == total_messages
            
            # Verify conversation history was cleared
            assert len(self.tracker._conversation_history) == 0

    def test_auto_track_agents(self):
        """Test automatic agent tracking."""
        mock_agent1 = Mock()
        mock_agent1.name = "Agent1"
        mock_agent1._llm_config = {"model": "gpt-4"}
        
        mock_agent2 = Mock()
        mock_agent2.name = "Agent2"
        mock_agent2._llm_config = {"model": "gpt-3.5-turbo"}
        
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
        mock_agent._llm_config = {"model": "gpt-4"}
        
        with patch.object(self.tracker, 'track_agent_creation') as mock_track:
            result = self.tracker.auto_track_agents(mock_agent)
            
            # Verify agent was tracked
            mock_track.assert_called_once()
            assert result == mock_agent

    def test_auto_track_agents_without_config(self):
        """Test automatic tracking of agents without llm_config."""
        mock_agent = Mock()
        mock_agent.name = "NoConfigAgent"
        # Remove _llm_config attribute completely
        if hasattr(mock_agent, '_llm_config'):
            delattr(mock_agent, '_llm_config')
        
        with patch.object(self.tracker, 'track_agent_creation') as mock_track:
            result = self.tracker.auto_track_agents(mock_agent)
            
            # Verify agent was stored but creation not tracked
            mock_track.assert_not_called()
            assert result == mock_agent
            assert len(self.tracker._tracked_agents) == 1