# Fifth Elephant MCP Server: A DIY Guide

This guide provides a complete walkthrough to create and run a simple Model Context Protocol (MCP) server from scratch.

## Table of Contents

1. [Prerequisites](#prerequisites)
   - [Install pyenv](#1-install-pyenv-if-not-already-installed)
   - [Install Python 3.11](#2-install-python-311)
   - [Install uv](#3-install-uv)
2. [Step 1: Project Setup](#step-1-project-setup)
3. [Step 2: Initialize a Python Project with uv](#step-2-initialize-a-python-project-with-uv)
4. [Step 3: Create and Activate Virtual Environment](#step-3-create-and-activate-virtual-environment)
5. [Step 4: Sync Dependencies (Not Required)](#step-4-sync-dependencies)
6. [Step 5: Add MCP Dependency](#step-5-add-mcp-dependency)
7. [Step 6: Verify Installation](#step-6-verify-installation)
8. [Step 7: Edit the Server Code](#step-7-edit-the-server-code)
9. [Step 8: Debug Locally with MCP Inspector](#step-8-debug-locally-with-mcp-inspector)
10. [Step 9: Configure Claude Desktop](#step-9-configure-claude-desktop)
11. [Troubleshooting](#troubleshooting)

## Prerequisites

Before we begin, ensure you have the following installed:

### 1. Install pyenv (if not already installed)

pyenv allows you to manage multiple Python versions easily.

**macOS:**
```sh
brew install pyenv
```

**Linux:**
```sh
curl https://pyenv.run | bash
```

**Windows:**
```powershell
# Install pyenv-win using PowerShell
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

Add pyenv to your shell profile:

**macOS/Linux (zsh):**
```sh
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc
```

**Windows:**
```powershell
# Restart your PowerShell or Command Prompt after installation
# pyenv-win will be automatically added to your PATH
```

### 2. Install Python 3.11

Install and set Python 3.11 as your local version:

```sh
pyenv install 3.11.9
pyenv local 3.11.9
```

Verify the Python version:
```sh
python --version
# Should output: Python 3.11.9
```

### 3. Install uv

Install [uv](https://github.com/astral-sh/uv) for fast Python package management:

**macOS/Linux:**
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify uv installation:
```sh
uv --version
```

## Step 1: Project Setup

First, create a directory for your project and navigate into it.

```sh
mkdir fifth-elephant-mcp
cd fifth-elephant-mcp
```

## Step 2: Initialize a Python Project with `uv`

Initialize a new Python project using `uv`. This will create a virtual environment and a `pyproject.toml` file.

```sh
uv init --quiet
```

## Step 3: Create and Activate Virtual Environment

Create a virtual environment using Python 3.11:

```sh
uv venv --python 3.11.9
```

Activate the virtual environment:

**macOS/Linux:**
```sh
source .venv/bin/activate
```


**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

Verify you're in the virtual environment (you should see `(.venv)` in your terminal prompt).

## Step 4: Sync Dependencies (not required)

Sync the project dependencies to ensure everything is up to date:

```sh
uv sync
```

## Step 5: Add MCP Dependency

Add the `mcp` library with CLI extras to your project's dependencies.

```sh
uv add "mcp[cli]"
```

**Note:** When installing MCP CLI, it may ask you to install additional dependencies. Press `y` to confirm.

## Step 6: Verify Installation

Verify that all components are properly installed:

```sh
# Verify Python version
python --version
# Should output: Python 3.11.9

# Verify uv version
uv --version

# Verify MCP library is installed (should be version 1.11 or later)
python -c "from mcp.server.fastmcp import __version__; print(__version__)"    
```

## Step 7: Edit the Server Code

When you ran `uv init`, a `main.py` file was already created. Edit this file and replace its contents with the following code. This code sets up a `FastMCP` server with two tools: `hello_world` and `add`.

```python
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Fifth Elephant")


# Add a hello world tool
@mcp.tool()
def hello_world() -> str:
    """Returns a friendly greeting."""
    return "hello world"


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Adds two numbers together."""
    return a + b


if __name__ == "__main__":
    mcp.run()
```

## Step 8: Debug Locally with MCP Inspector

For development and testing, you can use the MCP inspector.

Run the following command - 
```
uv run mcp dev main.py
```

This will spin up the inspector. It will open in your browser. Press connect on the left sidebar.

## Step 9: Configure Claude Desktop

If you haven't already, install Claude Desktop to use your MCP server:

1. Download Claude Desktop from [claude.ai](https://claude.ai/download)
2. Install and set up Claude Desktop

To use your MCP server with Claude Desktop, you need to configure it using absolute paths.

### Get Absolute Paths

First, get the absolute paths for your virtual environment's Python and your main.py file:

```sh
# Get the absolute path to your virtual environment's Python
which python

# Get the absolute path to your main.py file
pwd
```

**Windows (Command Prompt):**
```cmd
# Get the absolute path to your virtual environment's Python
where python

# Get the absolute path to your main.py file
cd
```

### Configure Claude Desktop

1. Open Claude Desktop
2. Go to Settings → Developer → Edit Config
3. Add your MCP server configuration to the `config.json` file:

**macOS/Linux:**
```json
{
  "mcpServers": {
    "fifth-elephant": {
      "command": "/absolute/path/to/your/.venv/bin/python",
      "args": ["/absolute/path/to/your/main.py"]
    }
  }
}
```

**Windows:**
```json
{
  "mcpServers": {
    "fifth-elephant": {
      "command": "C:\\absolute\\path\\to\\your\\.venv\\Scripts\\python.exe",
      "args": ["C:\\absolute\\path\\to\\your\\main.py"]
    }
  }
}
```

**Important:** 
- **macOS/Linux:** Replace `/absolute/path/to/your/.venv/bin/python` and `/absolute/path/to/your/main.py` with the actual absolute paths you obtained from the `which python` and `pwd` commands.
- **Windows:** Replace `C:\\absolute\\path\\to\\your\\.venv\\Scripts\\python.exe` and `C:\\absolute\\path\\to\\your\\main.py` with the actual absolute paths you obtained from the `where python` and `cd`/`Get-Location` commands. Note the double backslashes (`\\`) in Windows paths.

**Config file locations:**
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/claude/claude_desktop_config.json`

## Troubleshooting

If you encounter issues, try these common solutions:

### 1. Virtual Environment Issues

Make sure your virtual environment is activated:

**macOS/Linux:**
```sh
# Activate the virtual environment
source .venv/bin/activate

# Verify you're in the virtual environment
which python
# Should show: /path/to/your/project/.venv/bin/python
```


**Windows (Command Prompt):**
```cmd
# Activate the virtual environment
.venv\Scripts\activate.bat

# Verify you're in the virtual environment
where python
# Should show: C:\path\to\your\project\.venv\Scripts\python.exe
```

### 2. Dependency Issues

Sync your dependencies:
```sh
uv sync
```

### 3. MCP Inspector Configuration

If you're using the MCP inspector and having issues, use these settings:

- **Command:** `uv`
- **Args:** `run --with mcp mcp run main.py`

**Note:** The command should be `uv`, not `mcp-server-everything` or similar variants.

### 4. Path Issues

Ensure you're using absolute paths in your Claude Desktop configuration. Use:

**macOS/Linux:**
```sh
# Get absolute path to Python in your virtual environment
which python

# Get absolute path to your project directory
pwd
```


**Windows (Command Prompt):**
```cmd
# Get absolute path to Python in your virtual environment
where python

# Get absolute path to your project directory
cd
```

Then update your `config.json` with the complete absolute paths. Remember to use double backslashes (`\\`) for Windows paths in JSON.
