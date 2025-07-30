# Teraace Agentic Tracker

A comprehensive Python library for tracking AI agent events across 20 major agentic frameworks and sending them to the Teraace API for monitoring and analysis.

## 🚀 Features

- **20 Framework Support**: LangChain, CrewAI, AutoGPT, Swarm, LlamaIndex, AutoGen, Phidata, BabyAGI, MetaGPT, TaskWeaver, CAMEL, AgentGPT, SuperAGI, Semantic Kernel, Haystack, Rasa, PydanticAI, DSPy, Mirascope, Instructor
- **Unified Tracking**: Consistent event tracking across all frameworks
- **Production Ready**: Buffered delivery, async API client, graceful shutdown
- **Thread-Safe**: Safe for multi-threaded applications
- **Extensible**: Easy to add new framework integrations

## 📦 Teraace Account

Create your Teraace account at https://app.teraace.com/signup


## 📦 Installation

```bash
pip install teraace-tracker
```

## ⚡ Quick Start

### 1. Configuration

Create a `.env` file:

```env
TERAACE_API_KEY=your_api_key_here
TERAACE_BUFFER_SIZE=20
TERAACE_API_ENDPOINT=https://api.teraace.com/agents
TERAACE_REQUEST_TIMEOUT=30
TERAACE_MAX_RETRIES=3

```

### 2. Basic Usage

```python
from teraace_tracker import LangChainTracker

# Initialize tracker
tracker = LangChainTracker()

# Use with your LangChain agent
agent = initialize_agent(
    tools=your_tools,
    llm=llm,
    callbacks=[tracker]  # Add tracker as callback
)

# Use agent normally - events are tracked automatically
result = agent.run("What is 2 + 2?")
```

### 3. Other Frameworks
- **[AGENTS.md](AGENTS.md)** - Comprehensive examples for all 20 frameworks

```python
# CrewAI
from teraace_tracker import CrewAITracker
tracker = CrewAITracker()

# OpenAI Swarm
from teraace_tracker import SwarmTracker
tracker = SwarmTracker()

# LlamaIndex
from teraace_tracker import LlamaIndexTracker
tracker = LlamaIndexTracker()

# AutoGen
from teraace_tracker import AutoGenTracker
tracker = AutoGenTracker()

# And 11 more frameworks...
```

## 🎯 Supported Frameworks

| Framework | Status | Use Case |
|-----------|--------|----------|
| **LangChain** | ✅ | General-purpose agent framework |
| **CrewAI** | ✅ | Multi-agent collaboration |
| **AutoGPT** | ✅ | Autonomous task execution |
| **OpenAI Swarm** | ✅ | Multi-agent orchestration |
| **LlamaIndex** | ✅ | Data-centric agents & RAG |
| **AutoGen** | ✅ | Multi-agent conversations |
| **Phidata** | ✅ | Production AI assistants |
| **BabyAGI** | ✅ | Autonomous task prioritization |
| **MetaGPT** | ✅ | Software development teams |
| **TaskWeaver** | ✅ | Code-first stateful agents |
| **CAMEL** | ✅ | Communicative agent societies |
| **AgentGPT** | ✅ | Web-based autonomous agents |
| **SuperAGI** | ✅ | Open-source agent infrastructure |
| **Semantic Kernel** | ✅ | Microsoft AI orchestration |
| **Haystack** | ✅ | NLP/RAG with agents |
| **Rasa** | ✅ | Conversational AI |
| **PydanticAI** | ✅ | Production-grade AI applications |
| **DSPy** | ✅ | Prompt optimization framework |
| **Mirascope** | ✅ | Type-safe LLM toolkit |
| **Instructor** | ✅ | Structured data extraction |

## 📊 What Gets Tracked

- **Agent Lifecycle**: Creation, execution, completion
- **Tool Usage**: Function calls and results
- **Memory Operations**: Read, write, update operations
- **Multi-Agent Interactions**: Handoffs and collaboration
- **Code Generation**: Generated code and execution
- **Planning & Reasoning**: Agent thought processes
- **Resource Management**: File and data operations

## 🔧 Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `TERAACE_API_KEY` | Required | Your Teraace API key |
| `TERAACE_BUFFER_SIZE` | 20 | Events to buffer before sending |
| `TERAACE_API_ENDPOINT` | `https://api.teraace.com/agent-events` | API endpoint |

## 📚 Documentation

- **[AGENTS.md](AGENTS.md)** - Comprehensive examples for all 20 frameworks
- **[API Reference](docs/api.md)** - Detailed API documentation
- **[Configuration Guide](docs/config.md)** - Advanced configuration options

## 🛠️ Development

```bash
git clone https://github.com/teraace/teraace-tracker
cd teraace-tracker
pip install -e .[dev]
pytest
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.teraace.com](https://docs.teraace.com)
- **Email**: support@teraace.com
- **Issues**: [GitHub Issues](https://github.com/teraace/teraace-tracker/issues)