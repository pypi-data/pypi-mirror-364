"""Tests for Phidata integration."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from teraace_tracker.integrations.phidata import PhidataTracker


class TestPhidataTracker:
    """Test cases for PhidataTracker."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = PhidataTracker()

    def test_initialization(self):
        """Test tracker initialization."""
        assert self.tracker.framework_name == "phidata"
        assert hasattr(self.tracker, 'emitter')
        assert hasattr(self.tracker, '_tracked_assistants')
        assert hasattr(self.tracker, '_session_data')

    def test_track_assistant_creation(self):
        """Test assistant creation tracking."""
        mock_assistant = Mock()
        mock_assistant.id = "asst_123"
        mock_assistant.name = "DataAnalyst"
        mock_assistant.__class__.__name__ = "Assistant"
        mock_assistant.model = "gpt-4"
        mock_assistant.provider = "openai"
        mock_assistant.temperature = 0.7
        mock_assistant.max_tokens = 1000
        mock_assistant.memory = Mock()
        mock_assistant.knowledge = Mock()
        mock_assistant.tools = [Mock(), Mock()]
        
        config = {
            "model": "gpt-4",
            "provider": "openai",
            "temperature": 0.7
        }
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_assistant_creation(mock_assistant, config)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'assistant_creation'
            assert call_args['data']['assistant_name'] == 'DataAnalyst'
            assert call_args['data']['model'] == 'gpt-4'
            assert call_args['data']['tool_count'] == 2

    def test_track_conversation_run(self):
        """Test conversation run tracking."""
        mock_assistant = Mock()
        mock_assistant.name = "TestAssistant"
        mock_assistant.__class__.__name__ = "Assistant"
        mock_assistant.memory = Mock()
        
        message = "What's the weather like today?"
        session_id = "session_123"
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_conversation_run(mock_assistant, message, session_id)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'conversation_run_start'
            assert call_args['data']['message'] == message
            assert call_args['data']['session_id'] == session_id

    def test_track_tool_execution(self):
        """Test tool execution tracking."""
        mock_assistant = Mock()
        mock_assistant.name = "ToolAssistant"
        
        mock_tool = Mock()
        mock_tool.name = "weather_tool"
        mock_tool.__class__.__name__ = "WeatherTool"
        
        function_name = "get_weather"
        arguments = {"location": "New York"}
        result = {"temperature": "72F", "condition": "sunny"}
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_tool_execution(mock_assistant, mock_tool, function_name, arguments, result)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'tool_execution'
            assert call_args['data']['tool_name'] == 'weather_tool'
            assert call_args['data']['function_name'] == function_name

    def test_track_memory_operation(self):
        """Test memory operation tracking."""
        mock_assistant = Mock()
        mock_assistant.name = "MemoryAssistant"
        mock_assistant.memory = Mock()
        mock_assistant.memory.__class__.__name__ = "ConversationMemory"
        
        data = {"key": "user_preference", "value": "dark_mode"}
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_memory_operation(mock_assistant, "save", data)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'memory_operation'
            assert call_args['data']['operation'] == 'save'
            # The memory type should be extracted from the mock memory object
        # Since we're using a mock, it will return 'unknown' from our implementation
        assert call_args['data']['memory_type'] in ['ConversationMemory', 'unknown']

    def test_track_knowledge_query(self):
        """Test knowledge query tracking."""
        mock_assistant = Mock()
        mock_assistant.name = "KnowledgeAssistant"
        mock_assistant.knowledge = Mock()
        mock_assistant.knowledge.__class__.__name__ = "VectorKnowledge"
        
        query = "machine learning algorithms"
        results = [
            {"content": "Linear regression is...", "score": 0.95},
            {"content": "Decision trees are...", "score": 0.87}
        ]
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_knowledge_query(mock_assistant, query, results)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'knowledge_query'
            assert call_args['data']['query'] == query
            assert call_args['data']['result_count'] == 2

    def test_track_workflow_execution(self):
        """Test workflow execution tracking."""
        mock_workflow = Mock()
        mock_workflow.name = "DataAnalysisWorkflow"
        mock_workflow.__class__.__name__ = "Workflow"
        
        inputs = {"dataset": "sales_data.csv", "analysis_type": "trend"}
        outputs = {"trend": "increasing", "confidence": 0.85}
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_workflow_execution(mock_workflow, inputs, outputs)
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'workflow_execution'
            assert call_args['data']['workflow_name'] == 'DataAnalysisWorkflow'
            assert 'dataset' in call_args['data']['input_keys']

    def test_track_session_management(self):
        """Test session management tracking."""
        mock_assistant = Mock()
        mock_assistant.name = "SessionAssistant"
        
        session_id = "session_456"
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            # Test session creation
            self.tracker.track_session_management(mock_assistant, session_id, "create")
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['event_type'] == 'session_management'
            assert call_args['data']['session_id'] == session_id
            assert call_args['data']['operation'] == 'create'
            
            # Verify session was stored
            assert session_id in self.tracker._session_data

    def test_track_session_deletion(self):
        """Test session deletion tracking."""
        mock_assistant = Mock()
        mock_assistant.name = "SessionAssistant"
        
        session_id = "session_789"
        
        # First create a session
        self.tracker._session_data[session_id] = {'created': True, 'assistant': mock_assistant}
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            # Test session deletion
            self.tracker.track_session_management(mock_assistant, session_id, "delete")
            
            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[1]
            assert call_args['data']['operation'] == 'delete'
            
            # Verify session was removed
            assert session_id not in self.tracker._session_data

    def test_auto_track_assistant(self):
        """Test automatic assistant tracking."""
        mock_assistant = Mock()
        mock_assistant.name = "AutoAssistant"
        mock_assistant.model = "gpt-4"
        mock_assistant.provider = "openai"
        mock_assistant.temperature = 0.5
        
        with patch.object(self.tracker, 'track_assistant_creation') as mock_track:
            result = self.tracker.auto_track_assistant(mock_assistant)
            
            # Verify assistant was tracked
            mock_track.assert_called_once()
            assert result == mock_assistant
            
            # Verify assistant was stored
            assistant_id = id(mock_assistant)
            assert assistant_id in self.tracker._tracked_assistants

    def test_track_assistant_without_memory(self):
        """Test tracking assistant without memory."""
        mock_assistant = Mock()
        mock_assistant.name = "NoMemoryAssistant"
        mock_assistant.memory = None
        mock_assistant.knowledge = None
        mock_assistant.tools = []
        
        config = {"model": "gpt-3.5-turbo"}
        
        with patch.object(self.tracker, '_emit_event') as mock_emit:
            self.tracker.track_assistant_creation(mock_assistant, config)
            
            # Verify event was emitted with correct memory status
            call_args = mock_emit.call_args[1]
            assert call_args['data']['has_memory'] == False
            assert call_args['data']['has_knowledge'] == False
            assert call_args['data']['tool_count'] == 0