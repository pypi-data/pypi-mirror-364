"""
LangChain integration for Teraace tracker.
"""

import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish, LLMResult

from ..emitter import EventEmitter
from ..config import Config
from ..logging_util import logger


class LangChainTracker(BaseCallbackHandler):
    """LangChain callback handler for tracking agent events with workflow/graph support."""
    
    def __init__(
        self,
        workflow_name: Optional[str] = None,
        graph_name: Optional[str] = None,
        agent_name: Optional[str] = None,
        session_id: Optional[str] = None,
        config: Optional[Config] = None,
        run_env: str = "local",
        **metadata
    ):
        """
        Initialize LangChain tracker with flexible workflow/graph/agent support.
        
        Args:
            workflow_name: Name of the workflow (for multi-agent workflows)
            graph_name: Name of the LangGraph (alternative to workflow_name)
            agent_name: Name of the specific agent/node
            session_id: Session identifier (auto-generated if not provided)
            config: Teraace configuration
            run_env: Runtime environment ('local', 'cloud', etc.)
            **metadata: Additional metadata
        """
        super().__init__()
        
        # Store original parameters
        self.workflow_name = workflow_name
        self.graph_name = graph_name
        self.agent_name_only = agent_name
        self.metadata = metadata
        
        # Determine the primary identifier for tracking
        # Priority: workflow_name > graph_name > agent_name
        if workflow_name and agent_name:
            primary_name = f"{workflow_name}:{agent_name}"
        elif graph_name and agent_name:
            primary_name = f"{graph_name}:{agent_name}"
        elif workflow_name:
            primary_name = workflow_name
        elif graph_name:
            primary_name = graph_name
        elif agent_name:
            primary_name = agent_name
        else:
            primary_name = "langchain_agent"
        
        self.agent_name = primary_name
        self.session_id = session_id or str(uuid.uuid4())
        self.run_env = run_env
        self.emitter = EventEmitter(config)
        
        # Track ongoing operations
        self._run_start_times: Dict[str, float] = {}
        self._tool_calls: Dict[str, List] = {}
        self._memory_events: Dict[str, List] = {}
        
        logger.info(f"LangChain tracker initialized for agent '{self.agent_name}' session '{self.session_id}'")
    
    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: uuid.UUID,
        parent_run_id: Optional[uuid.UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Called when LLM starts running."""
        run_id_str = str(run_id)
        self._run_start_times[run_id_str] = time.time()
        self._tool_calls[run_id_str] = []
        self._memory_events[run_id_str] = []
        
        # Extract model name from serialized data
        model = self._extract_model_name(serialized)
        
        self.emitter.emit_agent_event(
            agent_name=self.agent_name,
            session_id=self.session_id,
            agent_framework="langchain",
            model=model,
            event_type="start",
            duration_ms=0,
            success=True,
            run_env=self.run_env
        )
        
        logger.debug(f"LLM started for run {run_id_str}")
    
    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: uuid.UUID,
        parent_run_id: Optional[uuid.UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when LLM ends running."""
        run_id_str = str(run_id)
        start_time = self._run_start_times.get(run_id_str, time.time())
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Extract model name from response
        model = self._extract_model_from_response(response)
        
        self.emitter.emit_agent_event(
            agent_name=self.agent_name,
            session_id=self.session_id,
            agent_framework="langchain",
            model=model,
            event_type="end",
            duration_ms=duration_ms,
            success=True,
            tool_calls=self._tool_calls.get(run_id_str, []),
            memory_events=self._memory_events.get(run_id_str, []),
            run_env=self.run_env
        )
        
        # Clean up tracking data
        self._cleanup_run_data(run_id_str)
        logger.debug(f"LLM ended for run {run_id_str}, duration: {duration_ms}ms")
    
    def on_llm_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        *,
        run_id: uuid.UUID,
        parent_run_id: Optional[uuid.UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when LLM encounters an error."""
        run_id_str = str(run_id)
        start_time = self._run_start_times.get(run_id_str, time.time())
        duration_ms = int((time.time() - start_time) * 1000)
        
        self.emitter.emit_agent_event(
            agent_name=self.agent_name,
            session_id=self.session_id,
            agent_framework="langchain",
            model="unknown",  # Model info may not be available on error
            event_type="error",
            duration_ms=duration_ms,
            success=False,
            exception=type(error).__name__,
            tool_calls=self._tool_calls.get(run_id_str, []),
            memory_events=self._memory_events.get(run_id_str, []),
            run_env=self.run_env
        )
        
        # Clean up tracking data
        self._cleanup_run_data(run_id_str)
        logger.debug(f"LLM error for run {run_id_str}: {type(error).__name__}")
    
    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: uuid.UUID,
        parent_run_id: Optional[uuid.UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Called when a tool starts running."""
        parent_run_id_str = str(parent_run_id) if parent_run_id else str(run_id)
        tool_name = serialized.get("name", "unknown_tool")
        
        tool_call = self.emitter.create_tool_call(tool_name)
        
        if parent_run_id_str in self._tool_calls:
            self._tool_calls[parent_run_id_str].append(tool_call)
        
        logger.debug(f"Tool '{tool_name}' started for run {parent_run_id_str}")
    
    def on_agent_action(
        self,
        action: AgentAction,
        *,
        run_id: uuid.UUID,
        parent_run_id: Optional[uuid.UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when agent takes an action."""
        parent_run_id_str = str(parent_run_id) if parent_run_id else str(run_id)
        
        tool_call = self.emitter.create_tool_call(action.tool)
        
        if parent_run_id_str in self._tool_calls:
            self._tool_calls[parent_run_id_str].append(tool_call)
        
        logger.debug(f"Agent action '{action.tool}' for run {parent_run_id_str}")
    
    def on_agent_finish(
        self,
        finish: AgentFinish,
        *,
        run_id: uuid.UUID,
        parent_run_id: Optional[uuid.UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when agent finishes."""
        logger.debug(f"Agent finished for run {run_id}")
    
    def _extract_model_name(self, serialized: Dict[str, Any]) -> str:
        """Extract model name from serialized LLM data."""
        # Try common model name fields
        model_fields = ["model_name", "model", "_type", "name"]
        
        for field in model_fields:
            if field in serialized:
                return str(serialized[field])
        
        # Try nested kwargs
        if "kwargs" in serialized:
            for field in model_fields:
                if field in serialized["kwargs"]:
                    return str(serialized["kwargs"][field])
        
        return "unknown"
    
    def _extract_model_from_response(self, response: LLMResult) -> str:
        """Extract model name from LLM response."""
        if hasattr(response, "llm_output") and response.llm_output:
            if "model_name" in response.llm_output:
                return response.llm_output["model_name"]
            if "model" in response.llm_output:
                return response.llm_output["model"]
        
        return "unknown"
    
    def _cleanup_run_data(self, run_id: str) -> None:
        """Clean up tracking data for a completed run."""
        self._run_start_times.pop(run_id, None)
        self._tool_calls.pop(run_id, None)
        self._memory_events.pop(run_id, None)
    
    async def flush_events(self) -> bool:
        """Manually flush all buffered events."""
        return await self.emitter.flush_events()
    
    def get_buffer_size(self) -> int:
        """Get current buffer size."""
        return self.emitter.get_buffer_size()
    
    @classmethod
    def auto_track_workflow(cls, workflow_name: str, agent_nodes: List[str], **tracker_kwargs):
        """
        Automatically set up tracking for a LangChain workflow with multiple agent nodes.
        This is the easiest way to get started - just specify the workflow and node names.
        """
        trackers = {}
        for node_name in agent_nodes:
            tracker = cls(workflow_name=workflow_name, agent_name=node_name, **tracker_kwargs)
            trackers[node_name] = tracker
        
        return trackers if len(agent_nodes) > 1 else trackers[agent_nodes[0]]
    
    @classmethod
    def auto_track_langgraph(cls, graph_name: str, node_names: List[str], **tracker_kwargs):
        """
        Automatically set up tracking for a LangGraph with multiple nodes.
        """
        trackers = {}
        for node_name in node_names:
            tracker = cls(graph_name=graph_name, agent_name=node_name, **tracker_kwargs)
            trackers[node_name] = tracker
        
        return trackers if len(node_names) > 1 else trackers[node_names[0]]
    
    def log_memory_event(self, event_type: str, key: str, run_id: Optional[str] = None):
        """Log a memory event for the current or specified run."""
        memory_event = self.emitter.create_memory_event(event_type, key)
        
        if run_id and run_id in self._memory_events:
            self._memory_events[run_id].append(memory_event)
        
        logger.debug(f"Memory {event_type} on key '{key}' for LangChain agent {self.agent_name}")