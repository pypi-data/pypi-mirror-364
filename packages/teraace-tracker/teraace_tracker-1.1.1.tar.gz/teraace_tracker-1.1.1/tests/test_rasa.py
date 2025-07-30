"""Tests for Rasa integration."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from teraace_tracker.integrations.rasa import RasaTracker


class TestRasaTracker:
    """Test cases for RasaTracker."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = RasaTracker("test_agent")

    def test_initialization(self):
        """Test tracker initialization."""
        assert self.tracker.framework_name == "rasa"
        assert hasattr(self.tracker, 'emitter')

    def test_track_intent_classification(self):
        """Test intent classification tracking."""
        mock_interpreter = Mock()
        mock_interpreter.__class__.__name__ = "RasaNLUInterpreter"
        
        message = {"text": "hello", "intent": {"name": "greet", "confidence": 0.95}}
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_intent_classification(mock_interpreter, "hello", message)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'intent_classification'
            assert call_args['data']['interpreter_type'] == 'RasaNLUInterpreter'
            assert call_args['data']['text'] == 'hello'
            assert call_args['data']['intent'] == 'greet'
            assert call_args['data']['confidence'] == 0.95

    def test_track_action_execution(self):
        """Test action execution tracking."""
        mock_action = Mock()
        mock_action.name.return_value = "action_greet"
        mock_action.__class__.__name__ = "ActionGreet"
        
        mock_tracker = Mock()
        mock_dispatcher = Mock()
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_action_execution(mock_action, mock_tracker, mock_dispatcher)
            
            # Verify event was emitted
            assert mock_emit.call_count >= 1
            call_args = mock_emit.call_args_list[0][1]
            assert call_args['event_type'] == 'action_execution_start'
            assert call_args['data']['action_name'] == 'action_greet'
            assert call_args['data']['action_type'] == 'ActionGreet'

    def test_track_dialogue_turn(self):
        """Test dialogue turn tracking."""
        mock_tracker = Mock()
        mock_tracker.sender_id = "user123"
        mock_tracker.latest_message = {"text": "hello", "intent": {"name": "greet"}}
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_dialogue_turn(mock_tracker, "user_message")
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'dialogue_turn'
            assert call_args['data']['sender_id'] == 'user123'
            assert call_args['data']['turn_type'] == 'user_message'

    def test_track_policy_prediction(self):
        """Test policy prediction tracking."""
        mock_policy = Mock()
        mock_policy.__class__.__name__ = "MemoizationPolicy"
        
        mock_tracker = Mock()
        mock_domain = Mock()
        prediction = {"action": "action_greet", "confidence": 0.8}
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_policy_prediction(mock_policy, mock_tracker, mock_domain, prediction)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'policy_prediction'
            assert call_args['data']['policy_type'] == 'MemoizationPolicy'
            assert call_args['data']['predicted_action'] == 'action_greet'
            assert call_args['data']['confidence'] == 0.8

    def test_track_form_execution(self):
        """Test form execution tracking."""
        mock_form = Mock()
        mock_form.name.return_value = "restaurant_form"
        mock_form.__class__.__name__ = "RestaurantForm"
        
        mock_tracker = Mock()
        mock_dispatcher = Mock()
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_form_execution(mock_form, mock_tracker, mock_dispatcher, "activate")
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'form_execution'
            assert call_args['data']['form_name'] == 'restaurant_form'
            assert call_args['data']['form_type'] == 'RestaurantForm'
            assert call_args['data']['operation'] == 'activate'

    def test_track_slot_setting(self):
        """Test slot setting tracking."""
        mock_tracker = Mock()
        mock_tracker.sender_id = "user123"
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_slot_setting(mock_tracker, "cuisine", "italian", "user")
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'slot_setting'
            assert call_args['data']['sender_id'] == 'user123'
            assert call_args['data']['slot_name'] == 'cuisine'
            assert call_args['data']['slot_value'] == 'italian'
            assert call_args['data']['source'] == 'user'

    def test_auto_track_agent(self):
        """Test automatic agent tracking."""
        mock_agent = Mock()
        
        # Test that auto_track_agent returns the agent
        result = self.tracker.auto_track_agent(mock_agent)
        assert result == mock_agent
        
        # Verify agent was stored
        assert hasattr(self.tracker, '_tracked_agent')
        assert self.tracker._tracked_agent == mock_agent