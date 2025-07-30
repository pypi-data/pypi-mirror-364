# Development Setup (Before PyPI Publishing)

This guide shows how to test your PhysioNet MCP server during development, before publishing to PyPI.

## 🚀 Quick Development Setup

### Option 1: Local Package Installation

**Step 1: Install in Editable Mode**
```bash
# From the project root directory
uv venv
uv pip install -e .
```

**Step 2: Claude Desktop Configuration**
```json
{
  "mcpServers": {
    "physionet-dev": {
      "command": "python",
      "args": ["/full/path/to/your/project/physionetmcp/cli.py", "run"],
      "db": ["aumc"],
      "dataRoot": "~/physionet_dev_data"
    }
  }
}
```

### Option 2: Direct Python Execution

**Claude Desktop Configuration:**
```json
{
  "mcpServers": {
    "physionet-dev": {
      "command": "python",
      "args": ["-m", "physionetmcp.cli", "run"],
      "cwd": "/path/to/your/physionetmcp/project",
      "db": ["aumc"],
      "dataRoot": "~/physionet_dev_data"
    }
  }
}
```

### Option 3: uv Script Mode

**Step 1: Create a Runner Script**
```bash
# Create bin/run-dev.py
#!/usr/bin/env python3
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import and run
from physionetmcp.cli import app
if __name__ == "__main__":
    app()
```

**Step 2: Claude Desktop Configuration**
```json
{
  "mcpServers": {
    "physionet-dev": {
      "command": "python",
      "args": ["/path/to/your/project/bin/run-dev.py", "run"],
      "db": ["aumc"],
      "dataRoot": "~/physionet_dev_data"
    }
  }
}
```

### Option 4: Local Wheel Testing

**Step 1: Build Local Wheel**
```bash
uv run python -m build
```

**Step 2: Test with Local Wheel**
```json
{
  "mcpServers": {
    "physionet-dev": {
      "command": "uv",
      "args": ["run", "--with", "/path/to/dist/physionetmcp-0.1.0-py3-none-any.whl", "physionetmcp", "run"],
      "db": ["aumc"],
      "dataRoot": "~/physionet_dev_data"
    }
  }
}
```

## 🧪 Development Workflow

### 1. Initial Setup
```bash
# Clone/create your project
git clone https://github.com/yourusername/physionetmcp
cd physionetmcp

# Set up development environment
uv venv
uv sync --dev

# Install in editable mode for development
uv pip install -e .
```

### 2. Development Testing
```bash
# Test CLI directly
python -m physionetmcp.cli --help
python -m physionetmcp.cli list-dbs

# Test individual components
python -c "from physionetmcp.database_registry import get_database_info; print(get_database_info('aumc'))"
```

### 3. MCP Testing with Inspector

Instead of Claude Desktop, use the MCP Inspector for development:

```bash
# Install MCP Inspector (if available)
npx @modelcontextprotocol/inspector

# Or use a simple stdio client
python test_client.py
```

**Simple Test Client (`test_client.py`):**
```python
import asyncio
import json
import subprocess
import sys

async def test_mcp_server():
    # Start the server process
    process = subprocess.Popen([
        sys.executable, "-m", "physionetmcp.cli", "run"
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Send initialization
    init_msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "0.1.0",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "0.1.0"},
            "db": ["aumc"],
            "dataRoot": "/tmp/physionet_test"
        }
    }
    
    process.stdin.write(json.dumps(init_msg) + "\n")
    process.stdin.flush()
    
    # Read response
    response = process.stdout.readline()
    print("Server response:", response.strip())
    
    process.terminate()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
```

## 🔧 Development Configuration Files

### pyproject.toml for Development
Make sure your `pyproject.toml` includes development dependencies:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0", 
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
    "build>=1.0.0",
    "twine>=4.0.0",
]

[project.scripts]
physionetmcp = "physionetmcp.cli:app"

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "black>=23.0.0", 
    "ruff>=0.1.0",
]
```

### VS Code Configuration

**.vscode/launch.json:**
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Run MCP Server",
            "type": "python",
            "request": "launch",
            "module": "physionetmcp.cli",
            "args": ["run"],
            "console": "integratedTerminal",
            "env": {
                "PHYSIONET_USERNAME": "your_username",
                "PHYSIONET_PASSWORD": "your_password"
            }
        }
    ]
}
```

## ✅ Testing Checklist

Before publishing, verify:

- [ ] Package installs correctly: `uv pip install -e .`
- [ ] CLI works: `python -m physionetmcp.cli --help`
- [ ] MCP server starts: Test with simple client
- [ ] Database registry loads: `python -c "from physionetmcp.database_registry import DATABASE_REGISTRY; print(len(DATABASE_REGISTRY))"`
- [ ] Configuration parsing works: Test with sample config
- [ ] Dependencies are correct: No missing imports
- [ ] Tests pass: `uv run pytest`
- [ ] Code quality: `uv run black . && uv run ruff check`

## 🚨 Common Development Issues

### Import Errors
```bash
# If you get "ModuleNotFoundError: No module named 'physionetmcp'"
# Make sure you're in the right directory and installed in editable mode
pwd  # Should be in the project root
uv pip install -e .
```

### Path Issues in Claude Desktop
```json
{
  "mcpServers": {
    "physionet-dev": {
      "command": "python",
      "args": ["/Users/your-username/code/physionetmcp/physionetmcp/cli.py", "run"],
      // Use absolute paths during development
    }
  }
}
```

### Environment Variables
```bash
# Set up development environment variables
export PHYSIONET_USERNAME="test_user"
export PHYSIONET_PASSWORD="test_pass"
export PYTHONPATH="/path/to/your/physionetmcp:$PYTHONPATH"
```

## 🎯 Ready for PyPI?

Once development testing is complete:

1. **Final testing**: Ensure everything works with local wheel
2. **Version bump**: Update version in `pyproject.toml`
3. **Documentation**: Update README with PyPI installation instructions
4. **Build**: `uv run python -m build`
5. **Publish**: Follow the [PUBLISHING.md](PUBLISHING.md) guide

After PyPI publication, users can use the simple:
```json
{
  "command": "uv",
  "args": ["run", "--with", "physionetmcp", "physionetmcp", "run"]
}
```

But during development, you'll use one of the direct Python execution methods above! 