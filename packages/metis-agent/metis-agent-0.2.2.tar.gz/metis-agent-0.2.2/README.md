# Metis Agent

![Metis Agent](https://img.shields.io/badge/Metis-Agent-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-Apache%202.0-blue)

A powerful, modular framework for building AI agents with minimal boilerplate code. Metis Agent provides a comprehensive toolkit for creating intelligent agents that can understand user queries, plan and execute complex tasks, and leverage specialized tools.

## Features

- **Modular Architecture**: Clean separation of concerns with specialized components
- **Multiple LLM Providers**: Seamless integration with OpenAI, Groq, Anthropic, and HuggingFace
- **Secure API Key Management**: Safely store and retrieve API keys
- **Advanced Memory Systems**: 
  - SQLite-based persistent memory
  - Titans-inspired adaptive memory with context-aware retrieval
- **Specialized Tools**: Ready-to-use tools for common tasks:
  - Code generation
  - Content creation
  - Web search
  - Web scraping (Firecrawl integration)
- **Task Planning and Execution**: Break down complex tasks into manageable subtasks
- **Intent Classification**: Automatically determine if a query is a question or task
- **Multiple Interfaces**: 
  - Python API for direct integration
  - Command-line interface for quick access
  - Web server for API-based interaction

## 📦 Installation

```bash
pip install metis-agent
```

## Quick Start

### Basic Usage

```python
from metis_agent import SingleAgent

# Create an agent
agent = SingleAgent()

# Process a query
response = agent.process_query("Write a Python function to calculate Fibonacci numbers")
print(response)
```

### Using Different LLM Providers

```python
from metis_agent import SingleAgent, configure_llm

# Configure LLM (OpenAI, Groq, Anthropic, or HuggingFace)
configure_llm("groq", "llama-3.1-8b-instant", "your-api-key")

# Create an agent
agent = SingleAgent()

# Process a query
response = agent.process_query("Explain quantum computing in simple terms")
print(response)
```

### Creating Custom Tools

```python
from metis_agent import SingleAgent, BaseTool, register_tool

class MyCustomTool(BaseTool):
    name = "custom_tool"
    description = "A custom tool for specialized tasks"
    
    def can_handle(self, task):
        return "custom task" in task.lower()
        
    def execute(self, task):
        return f"Executed custom tool on: {task}"

# Register the tool
register_tool("custom_tool", MyCustomTool)

# Create an agent
agent = SingleAgent()

# Process a query
response = agent.process_query("Perform a custom task")
print(response)
```

### Using Titans Memory

```python
from metis_agent import SingleAgent

# Create an agent with Titans memory
agent = SingleAgent(use_titans_memory=True)

# Process queries with memory
result1 = agent.process_query("What is machine learning?", session_id="user123")
result2 = agent.process_query("How does it relate to AI?", session_id="user123")
```

## 🖥️ Command Line Interface

Metis Agent provides a comprehensive command-line interface:

```bash
# Run a query
metis run "Write a Python function to calculate Fibonacci numbers"

# Run with specific LLM
metis run "Explain quantum computing" --llm groq --model llama-3.1-8b-instant

# Start the web server
metis serve --port 5000 --memory

# List available tools
metis tools list

# Show memory statistics
metis memory stats

# Set an API key
metis auth set-key openai your-api-key

# List configured API keys
metis auth list-keys

# Configure default LLM
metis configure-llm --provider groq --model llama-3.1-8b-instant
```

## 🌐 Web Server

Metis Agent includes a web server for API access:

```bash
# Start the web server
metis serve
```

Then make requests to the API:

```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Write a Python function to calculate Fibonacci numbers"}'
```

API Endpoints:

- `GET /` - Server status
- `POST /api/query` - Process a query
- `GET /api/agent-identity` - Get agent information
- `GET /api/memory-insights` - Get memory statistics
- `GET /api/tools` - List available tools

## 📚 Detailed Documentation

### Core Components

#### SingleAgent

The main agent class that orchestrates all components:

```python
from metis_agent import SingleAgent

agent = SingleAgent(
    use_titans_memory=False,  # Enable/disable Titans memory
    tools=None,               # Custom tools (uses all available if None)
    llm_provider="openai",    # LLM provider
    llm_model=None,           # LLM model (uses default if None)
    memory_path=None,         # Path to memory database
    task_file=None            # Path to task file
)
```

#### Intent Router

Determines whether a user query is a question or a task:

```python
from metis_agent.core.intent_router import IntentRouter

router = IntentRouter()
intent = router.classify("What is the capital of France?")  # Returns "question"
intent = router.classify("Create a Python script to sort a list")  # Returns "task"
```

#### Task Manager

Manages tasks and their status:

```python
from metis_agent.core.task_manager import TaskManager

task_manager = TaskManager()
task_manager.add_task("Write a function to calculate Fibonacci numbers")
task_manager.mark_complete("Write a function to calculate Fibonacci numbers")
tasks = task_manager.get_all_tasks()
```

#### Memory Systems

SQLite-based memory:

```python
from metis_agent.memory.sqlite_store import SQLiteMemory

memory = SQLiteMemory("memory.db")
memory.store_input("user123", "What is machine learning?")
memory.store_output("user123", "Machine learning is...")
context = memory.get_context("user123")
```

Titans-inspired adaptive memory:

```python
from metis_agent.memory.titans.titans_memory import TitansInspiredMemory

memory = TitansInspiredMemory("memory_dir")
memory.store_memory("Machine learning is...", "ai_concepts")
relevant_memories = memory.retrieve_relevant_memories("What is deep learning?")
```

### LLM Providers

Configure and use different LLM providers:

```python
from metis_agent.core.llm_interface import configure_llm, get_llm

# Configure LLM
configure_llm("openai", "gpt-4o")  # OpenAI
configure_llm("groq", "llama-3.1-8b-instant")  # Groq
configure_llm("anthropic", "claude-3-opus-20240229")  # Anthropic
configure_llm("huggingface", "mistralai/Mixtral-8x7B-Instruct-v0.1")  # HuggingFace

# Get configured LLM
llm = get_llm()
response = llm.chat([{"role": "user", "content": "Hello!"}])
```

### Tools

Available tools:

- `CodeGenerationTool`: Generates code based on requirements
- `ContentGenerationTool`: Creates various types of content
- `GoogleSearchTool`: Performs web searches
- `FirecrawlTool`: Scrapes and analyzes web content

Creating custom tools:

```python
from metis_agent.tools.base import BaseTool
from metis_agent.tools.registry import register_tool

class MyTool(BaseTool):
    name = "my_tool"
    description = "Custom tool for specific tasks"
    
    def can_handle(self, task):
        # Determine if this tool can handle the task
        return "specific task" in task.lower()
        
    def execute(self, task):
        # Execute the task
        return f"Task executed: {task}"

# Register the tool
register_tool("my_tool", MyTool)
```

### API Key Management

Secure storage and retrieval of API keys:

```python
from metis_agent.auth.api_key_manager import APIKeyManager

key_manager = APIKeyManager()
key_manager.set_key("openai", "your-api-key")
api_key = key_manager.get_key("openai")
services = key_manager.list_services()
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run system tests
python metis_agent/test_system.py

# Run CLI tests
python metis_agent/test_cli.py
```

## 🔄 Advanced Usage

### Session Management

Maintain context across multiple interactions:

```python
agent = SingleAgent()

# First query
response1 = agent.process_query(
    "What are the main types of machine learning?",
    session_id="user123"
)

# Follow-up query (uses context from first query)
response2 = agent.process_query(
    "Can you explain supervised learning in more detail?",
    session_id="user123"
)
```

### Tool Selection

Specify which tool to use for a query:

```python
agent = SingleAgent()

# Use a specific tool
response = agent.process_query(
    "Generate a Python function to sort a list",
    tool_name="CodeGenerationTool"
)
```

### Memory Insights

Get insights about the agent's memory:

```python
agent = SingleAgent(use_titans_memory=True)

# Process some queries
agent.process_query("What is machine learning?", session_id="user123")
agent.process_query("Explain neural networks", session_id="user123")

# Get memory insights
insights = agent.get_memory_insights()
print(insights)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

Project Link: [https://github.com/yourusername/metis-agent](https://github.com/yourusername/metis-agent)

---

<p align="center">
  <strong>Metis Agent - Building Intelligent AI Systems</strong>
</p>