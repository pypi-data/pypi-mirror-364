"""
Teraace Agentic Tracker - A Python library for tracking AI agent events.
"""

__version__ = "0.1.0"
__author__ = "Teraace"

from .event_models import ToolCall, MemoryEvent, AgentEvent
from .emitter import EventEmitter
from .buffer import EventBuffer
from .client import TeraaceAPIClient
from .config import Config
from .integrations import (
    LangChainTracker, CrewAITracker, AutoGPTTracker,
    SemanticKernelTracker, HaystackTracker, RasaTracker,
    SwarmTracker, LlamaIndexTracker, AutoGenTracker, PhiDataTracker,
    BabyAGITracker, MetaGPTTracker, TaskWeaverTracker,
    CAMELTracker, AgentGPTTracker, SuperAGITracker,
    PydanticAITracker, DSPyTracker, MirascopeTracker, InstructorTracker
)
from .integrations.base import BaseTracker, IntegrationRegistry, register_integration

__all__ = [
    "ToolCall",
    "MemoryEvent", 
    "AgentEvent",
    "EventEmitter",
    "EventBuffer",
    "TeraaceAPIClient",
    "Config",
    "LangChainTracker",
    "CrewAITracker", 
    "AutoGPTTracker",
    "SemanticKernelTracker",
    "HaystackTracker",
    "RasaTracker",
    "SwarmTracker",
    "LlamaIndexTracker",
    "AutoGenTracker",
    "PhiDataTracker",
    "BabyAGITracker",
    "MetaGPTTracker",
    "TaskWeaverTracker",
    "CAMELTracker",
    "AgentGPTTracker",
    "SuperAGITracker",
    "PydanticAITracker",
    "DSPyTracker",
    "MirascopeTracker",
    "InstructorTracker",
    "BaseTracker",
    "IntegrationRegistry",
    "register_integration"
]