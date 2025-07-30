# EQUITR Coder

**Advanced Multi-Agent AI Coding Assistant with Strategic Supervision**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Textual TUI](https://img.shields.io/badge/TUI-Textual-green.svg)](https://textual.textualize.io/)

EQUITR Coder is a sophisticated AI coding assistant that combines **weak specialized workers** with a **strong reasoning supervisor** to create an intelligent, hierarchical system for software development. From simple single-agent tasks to complex multi-agent coordination, EQUITR Coder provides clean APIs, advanced TUI, and comprehensive tooling for modern AI-assisted development.

## 🌟 Key Features

### 🧠 **Hierarchical Intelligence System**
- **Strong Supervisor**: GPT-4/Claude for strategic guidance and architectural decisions
- **Weak Workers**: Specialized agents (GPT-3.5/smaller models) for efficient task execution
- **ask_supervisor Tool**: Workers can consult the supervisor for complex problems

### 🔧 **Multiple Interface Modes**
- **Programmatic**: Clean OOP interface following Python standards
- **Advanced TUI**: Rich terminal interface with live updates, parallel agent views, and real-time monitoring
- **CLI**: Command-line interface for single/multi-agent execution
- **API**: RESTful FastAPI server for integration

### 🔒 **Enterprise-Grade Security**
- Restricted file system access per worker
- Tool whitelisting and permission control
- Cost limits and iteration bounds
- Session isolation and audit trails

### 📊 **Comprehensive Monitoring**
- Real-time cost tracking across all agents
- Todo list progress monitoring
- Git integration with automatic commits
- Session management and history

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install -e .

# With advanced TUI support
pip install -e .[all]

# Development installation
pip install -e .[dev]
```

### Environment Setup

```bash
# Required: Set your API key
export OPENAI_API_KEY="your-openai-key"
# OR
export ANTHROPIC_API_KEY="your-anthropic-key"

# Optional: Configure defaults
export EQUITR_MODE="single"          # or "multi"
export EQUITR_MAX_COST="5.0"
export EQUITR_MODEL="gpt-4"
```

## 💻 Usage Modes

### 1. Programmatic Interface (Recommended)

The cleanest way to integrate EQUITR Coder into your applications:

```python
import asyncio
from equitrcoder import EquitrCoder, TaskConfiguration

async def main():
    # Create coder instance
    coder = EquitrCoder(mode="single", git_enabled=True)
    
    # Configure task
    config = TaskConfiguration(
        description="Analyze and improve code",
        max_cost=2.0,
        max_iterations=15,
        auto_commit=True
    )
    
    # Execute task
    result = await coder.execute_task(
        "Analyze the codebase and add comprehensive type hints",
        config=config
    )
    
    # Check results
    if result.success:
        print(f"✅ Success! Cost: ${result.cost:.4f}")
        if result.git_committed:
            print(f"📝 Committed: {result.commit_hash}")
    
    await coder.cleanup()

asyncio.run(main())
```

#### Multi-Agent Example

```python
from equitrcoder import create_multi_agent_coder, MultiAgentTaskConfiguration

async def multi_agent_example():
    # Create multi-agent system
    coder = create_multi_agent_coder(
        max_workers=3,
        supervisor_model="gpt-4",
        worker_model="gpt-3.5-turbo"
    )
    
    # Configure complex task
    config = MultiAgentTaskConfiguration(
        description="Full-stack development",
        max_workers=3,
        max_cost=10.0,
        auto_commit=True
    )
    
    # Execute complex task with multiple workers
    result = await coder.execute_task(
        "Build a complete user authentication system with database, API, and frontend",
        config=config
    )
    
    print(f"Workers used: {result.iterations}")
    print(f"Total cost: ${result.cost:.4f}")
    
    await coder.cleanup()
```

### 2. Advanced TUI Mode

Rich terminal interface with real-time monitoring:

```bash
# Launch single-agent TUI
equitrcoder tui --mode single

# Launch multi-agent TUI  
equitrcoder tui --mode multi
```

**TUI Features:**
- 📊 **Bottom Status Bar**: Shows mode, models, stage, agent count, and cost
- 📋 **Left Todo Sidebar**: Real-time todo progress with priority indicators
- 💬 **Center Chat Window**: Live agent outputs with syntax highlighting
- 🪟 **Parallel Agent Tabs**: Split windows for multiple agents
- ⌨️ **Keyboard Controls**: Enter to execute, Ctrl+C to quit

### 3. Command Line Interface

Direct task execution from command line:

```bash
# Single agent mode
equitrcoder single "Fix the authentication bug in user.py" \
  --model gpt-4 \
  --max-cost 2.0 \
  --max-iterations 20

# Multi-agent mode  
equitrcoder multi "Build a complete web application with authentication" \
  --workers 3 \
  --supervisor-model gpt-4 \
  --worker-model gpt-3.5-turbo \
  --max-cost 15.0

# Tool management
equitrcoder tools --list
equitrcoder tools --discover
```

### 4. API Server

RESTful API for integration:

```bash
# Start API server
equitrcoder api --host localhost --port 8000

# Execute tasks via HTTP
curl -X POST http://localhost:8000/execute_task \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Add unit tests to the project",
    "mode": "single",
    "max_cost": 2.0
  }'
```

## 🧠 ask_supervisor Tool

The `ask_supervisor` tool is the key to EQUITR Coder's intelligence hierarchy. Worker agents can consult the strong supervisor model for:

- **Architectural Decisions**: "Should I use JWT or sessions for auth?"
- **Complex Debugging**: "How do I troubleshoot this intermittent database error?"
- **Code Review**: "Is this implementation following best practices?"
- **Strategic Planning**: "What's the best approach for this refactoring?"

### Example Worker Usage

```python
# Worker agent automatically has access to ask_supervisor in multi-agent mode
await worker.call_tool("ask_supervisor", 
    question="I need to implement caching. What approach should I take for a high-traffic web API?",
    context_files=["src/api.py", "requirements.txt"],
    include_repo_tree=True
)
```

The supervisor provides structured guidance:
- **Strategic Analysis**: Core challenges and trade-offs
- **Recommended Approach**: Step-by-step implementation plan
- **Architectural Considerations**: How it fits the broader codebase
- **Risk Assessment**: Potential issues and mitigation strategies
- **Next Steps**: Immediate actionable items

## 🔧 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    EQUITR CODER SYSTEM                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐                ┌─────────────────┐    │
│  │   SUPERVISOR    │◄──────────────►│   SUPERVISOR    │    │
│  │ (Strong Model)  │  ask_supervisor │ (Strong Model)  │    │
│  │   GPT-4/Claude  │                │   GPT-4/Claude  │    │
│  └─────────────────┘                └─────────────────┘    │
│           │                                   │            │
│           ▼                                   ▼            │
│  ┌─────────────────┐                ┌─────────────────┐    │
│  │ WORKER AGENT 1  │◄──messaging───►│ WORKER AGENT 2  │    │
│  │  (Weak Model)   │                │  (Weak Model)   │    │
│  │ GPT-3.5/Smaller │                │ GPT-3.5/Smaller │    │
│  └─────────────────┘                └─────────────────┘    │
│           │                                   │            │
│           ▼                                   ▼            │
│  ┌─────────────────┐                ┌─────────────────┐    │
│  │ RESTRICTED FS   │                │ RESTRICTED FS   │    │
│  │   Tools/Scope   │                │   Tools/Scope   │    │
│  └─────────────────┘                └─────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### Agents
- **BaseAgent**: Core functionality (messaging, tools, cost tracking, session management)  
- **WorkerAgent**: Adds restricted file system access and tool whitelisting for security

#### Orchestrators
- **SingleAgentOrchestrator**: Simple wrapper for single-agent tasks with session management
- **MultiAgentOrchestrator**: Advanced coordination with parallel execution and supervisor oversight

#### Security Features
- **RestrictedFileSystem**: Path-based access control with traversal protection
- **Tool Whitelisting**: Fine-grained permission control per worker
- **Cost Limits**: Per-agent and global cost tracking and limits
- **Session Isolation**: Separate contexts for different workflows

## 🛠️ Tool System

EQUITR Coder has an extensible plugin architecture:

### Built-in Tools

```python
# File operations (with security restrictions for WorkerAgent)
await worker.call_tool("read_file", file_path="src/main.py")
await worker.call_tool("edit_file", file_path="src/main.py", content="new content")

# Git operations with auto-commit
await worker.call_tool("git_commit", message="Fix authentication bug")

# Shell commands
await worker.call_tool("run_cmd", cmd="pytest tests/")

# Supervisor consultation (multi-agent only)
await worker.call_tool("ask_supervisor", 
                      question="Should I refactor this function?",
                      context_files=["src/auth.py"])

# Todo management
await worker.call_tool("create_todo", description="Add unit tests", priority="high")
```

### Custom Tools

```python
from equitrcoder.tools.base import Tool, ToolResult
from pydantic import BaseModel, Field

class MyCustomArgs(BaseModel):
    input_text: str = Field(..., description="Text to process")

class MyCustomTool(Tool):
    def get_name(self) -> str:
        return "my_custom_tool"
    
    def get_description(self) -> str:
        return "Description of what this tool does"
    
    def get_args_schema(self) -> type[BaseModel]:
        return MyCustomArgs
    
    async def run(self, **kwargs) -> ToolResult:
        args = MyCustomArgs(**kwargs)
        # Tool logic here
        return ToolResult(success=True, data="Result")

# Register the tool
from equitrcoder.tools import registry
registry.register(MyCustomTool())
```

## 📚 Documentation

- **[Ask Supervisor Guide](equitrcoder/docs/ASK_SUPERVISOR_GUIDE.md)**: Complete guide to the supervisor consultation system
- **[Programmatic Usage](equitrcoder/docs/PROGRAMMATIC_USAGE_GUIDE.md)**: Comprehensive programmatic API documentation
- **[Configuration Guide](equitrcoder/docs/CONFIGURATION_GUIDE.md)**: System configuration options
- **[Development Setup](equitrcoder/docs/DEVELOPMENT_SETUP.md)**: Contributing and development guide
- **[Tool System](equitrcoder/docs/TOOL_LOGGING_AND_MULTI_MODEL_GUIDE.md)**: Tool development and logging

## 🎯 Examples

Run the comprehensive examples:

```bash
# Programmatic interface examples
cd equitrcoder/examples
python programmatic_example.py

# Multi-agent coordination
python multi_agent_coordination.py

# Custom tool development
python tool_logging_example.py
```

## 🔒 Security & Cost Management

### File System Security
```python
# Workers operate in restricted environments
worker = WorkerAgent(
    worker_id="frontend_dev",
    scope_paths=["src/frontend/", "public/"],  # Only access these paths
    allowed_tools=["read_file", "edit_file"],  # Limited tool set
    max_cost=2.0  # Cost boundary
)
```

### Cost Controls
```python
# Global cost limits
orchestrator = MultiAgentOrchestrator(
    global_cost_limit=10.0,  # Total spending cap
    max_concurrent_workers=3  # Resource limits
)

# Per-task limits
config = TaskConfiguration(
    max_cost=1.0,           # Task-specific limit
    max_iterations=20       # Iteration boundary
)
```

### Git Integration
```python
# Automatic commit management
coder = EquitrCoder(git_enabled=True)

config = TaskConfiguration(
    auto_commit=True,
    commit_message="AI-assisted feature implementation"
)

# Every successful task gets committed with metadata
result = await coder.execute_task("Add authentication", config)
if result.git_committed:
    print(f"Committed as: {result.commit_hash}")
```

## 🚀 Advanced Patterns

### Retry Logic with Escalating Resources
```python
async def robust_execution(task_description, max_retries=3):
    for attempt in range(max_retries):
        config = TaskConfiguration(
            max_cost=1.0 * (attempt + 1),      # Increase cost limit
            max_iterations=10 * (attempt + 1)  # Increase iterations
        )
        
        result = await coder.execute_task(task_description, config)
        if result.success:
            return result
        
        await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    return None  # All attempts failed
```

### Session-Based Development
```python
# Continue previous work
config = TaskConfiguration(
    session_id="auth_development",
    description="Authentication system development"
)

# Each task builds on previous context
await coder.execute_task("Design user authentication schema", config)
await coder.execute_task("Implement login endpoint", config)  
await coder.execute_task("Add password validation", config)

# Review session history
session = coder.get_session_history("auth_development")
print(f"Total cost: ${session.cost:.4f}")
```

### Multi-Worker Coordination
```python
# Specialized workers for different domains
frontend_worker = WorkerConfiguration(
    worker_id="ui_specialist",
    scope_paths=["src/frontend/", "assets/"],
    allowed_tools=["read_file", "edit_file", "run_cmd"]
)

backend_worker = WorkerConfiguration(
    worker_id="api_specialist", 
    scope_paths=["src/backend/", "database/"],
    allowed_tools=["read_file", "edit_file", "run_cmd", "git_commit"]
)

# Parallel execution with automatic coordination
tasks = [
    {"task_id": "ui", "worker_id": "ui_specialist", "task_description": "Build login UI"},
    {"task_id": "api", "worker_id": "api_specialist", "task_description": "Build auth API"}
]

results = await coder.execute_parallel_tasks(tasks)
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes with proper tests
4. **Commit** your changes (`git commit -m 'Add amazing feature'`)
5. **Push** to the branch (`git push origin feature/amazing-feature`)
6. **Open** a Pull Request

See [DEVELOPMENT_SETUP.md](equitrcoder/docs/DEVELOPMENT_SETUP.md) for detailed setup instructions.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** and **Anthropic** for providing the language models
- **Textual** for the advanced terminal UI framework
- **LiteLLM** for unified model interface
- **FastAPI** for the API server capabilities

---

**EQUITR Coder**: Where strategic intelligence meets tactical execution. 🧠⚡ 