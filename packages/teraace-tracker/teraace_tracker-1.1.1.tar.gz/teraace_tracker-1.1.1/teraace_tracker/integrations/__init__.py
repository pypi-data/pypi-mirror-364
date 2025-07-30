"""
Integrations for various AI agent frameworks.
"""

from .langchain import LangChainTracker
from .crewai import CrewAITracker
from .autogpt import AutoGPTTracker
from .semantic_kernel import SemanticKernelTracker
from .haystack import HaystackTracker
from .rasa import RasaTracker
from .swarm import SwarmTracker
from .llamaindex import LlamaIndexTracker
from .autogen import AutoGenTracker
from .phidata import PhiDataTracker
from .babyagi import BabyAGITracker
from .metagpt import MetaGPTTracker
from .taskweaver import TaskWeaverTracker
from .camel import CAMELTracker
from .agentgpt import AgentGPTTracker
from .superagi import SuperAGITracker
from .pydantic_ai import PydanticAITracker
from .dspy import DSPyTracker
from .mirascope import MirascopeTracker
from .instructor import InstructorTracker
from .base import BaseTracker, IntegrationRegistry, register_integration

__all__ = [
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