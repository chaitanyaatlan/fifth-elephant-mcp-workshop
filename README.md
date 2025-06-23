# Fifth Elephant MCP Server: A DIY Guide

This guide provides a complete walkthrough to create and run a simple Model Context Protocol (MCP) server from scratch.

## Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) installed.

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

## Step 3: Add MCP Dependency

Add the `mcp` library with CLI extras to your project's dependencies.

```sh
uv add "mcp[cli]"
```

## Step 4: Create the Server Code

Create a file named `main.py` and paste the following code into it. This code sets up a `FastMCP` server with two tools: `hello_world` and `add`.

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

## Step 5: Run the Server

You can now run your MCP server.

### Option A: Direct Execution

Run the server directly using `uv`.

```sh
uv run python main.py
```

### Option B: Using the MCP Inspector

The MCP development tools include an inspector for testing your server.

```sh
uv run mcp dev main.py
```

The server is now running and ready to be interacted with by an MCP client.
