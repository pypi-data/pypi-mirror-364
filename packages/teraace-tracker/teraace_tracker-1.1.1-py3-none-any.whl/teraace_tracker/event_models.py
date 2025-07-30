"""
Pydantic models for Teraace agent events.
"""

from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import uuid


class ToolCall(BaseModel):
    """Model for tool call events."""
    tool_name: str = Field(..., description="Name of the tool that was called")
    timestamp: datetime = Field(..., description="When the tool was called")


class MemoryEvent(BaseModel):
    """Model for memory operation events."""
    event_type: str = Field(..., description="Type of memory operation: 'read', 'write', or 'update'")
    key: str = Field(..., description="Memory key that was accessed")
    timestamp: datetime = Field(..., description="When the memory operation occurred")


class AgentEvent(BaseModel):
    """Model for agent lifecycle events."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique event identifier")
    agent_name: str = Field(..., description="Logical name/label for the agent")
    session_id: str = Field(..., description="Unique identifier per run/session")
    agent_framework: str = Field(..., description="Framework used: 'langchain', 'crewai', or 'autogpt'")
    model: str = Field(..., description="Model name e.g., 'gpt-4o', 'claude-3'")
    runtime: str = Field(..., description="Runtime environment e.g., 'python3.10/ubuntu'")
    run_env: str = Field(..., description="Execution environment: 'local', 'cloud', or other")
    event_type: str = Field(..., description="Event type: 'start', 'end', or 'error'")
    timestamp: datetime = Field(..., description="When the event occurred")
    duration_ms: int = Field(..., description="Duration in milliseconds for the event")
    success: bool = Field(..., description="True if successful, False otherwise")
    exception: str = Field(default="", description="Empty if none, else exception type/class")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="List of tool calls")
    memory_events: List[MemoryEvent] = Field(default_factory=list, description="List of memory events")