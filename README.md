# Building a Simple Todoist MCP Server: DIY Guide

A complete beginner-friendly tutorial for creating your first MCP server that connects Claude Desktop to Todoist. Learn to build AI integrations with clean, simple code!

## 🎯 What You'll Build

A super simple MCP server that gives Claude Desktop these Todoist tools:
- **Create Task**: Add new tasks with descriptions, due dates, and priorities
- **Get Tasks**: Retrieve and filter your tasks 
- **Update Task**: Modify existing tasks
- **Complete Task**: Mark tasks as done
- **Delete Task**: Remove tasks permanently
- **Find Task**: Search tasks by content
- **Get Projects**: List all your Todoist projects

## 🏗️ Simple Project Structure

We keep it minimal and beginner-friendly:

```
todoist-mcp-server/
├── main.py           # FastMCP server with @mcp.tool() functions
├── apis.py           # Simple Todoist API calls
├── utils.py          # Basic validation helpers
├── pyproject.toml    # Dependencies
├── .env              # Your API token (you'll create this)
└── README.md         # This guide
```

### 🧱 Why This Structure?

**Super Simple**: Each file has one clear job:
- `main.py`: Define tools for Claude using `@mcp.tool()` decorators
- `apis.py`: Make API calls to Todoist and return simple data
- `utils.py`: Validate inputs (just 3 simple functions!)

**Beginner-Friendly**: No complex patterns, no excessive error handling, no confusing abstractions.

---

## 📋 Prerequisites

1. **Python 3.11+** 
2. **A Todoist account** (free works!)
3. **UV package manager** (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
4. **Claude Desktop** app

---

## 🚀 Step 1: Project Setup

### Create Project

```bash
mkdir todoist-mcp-server
cd todoist-mcp-server
uv init
```

### Install Dependencies

```bash
uv add "mcp[cli]"
uv add "todoist-api-python"
uv add "python-dotenv"
```

### Get Your Todoist API Token

1. Go to [Todoist Settings > Integrations](https://todoist.com/prefs/integrations)
2. Copy your API token
3. Create `.env` file:

```bash
# .env
TODOIST_API_TOKEN=your_token_here
```

---

## 🔧 Step 2: Build the API Layer (`apis.py`)

This file talks to Todoist. Keep it simple!

```python
"""
Simple Todoist API Functions
"""

import os
from typing import List, Optional
from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("TODOIST_API_TOKEN")
todoist_client = None


def initialize_todoist_client():
    """Initialize the Todoist API client."""
    global todoist_client
    if not API_TOKEN:
        raise Exception("TODOIST_API_TOKEN not set")
    todoist_client = TodoistAPI(API_TOKEN)


def create_task_in_todoist(content: str, description: Optional[str] = None, 
                          due_string: Optional[str] = None, priority: Optional[int] = None) -> dict:
    """Create a new task and return its data."""
    if not todoist_client:
        initialize_todoist_client()
    
    task: Task = todoist_client.add_task(
        content=content,
        description=description,
        due_string=due_string,
        priority=priority
    )
    
    return {
        "id": task.id,
        "content": task.content,
        "description": task.description,
        "priority": task.priority,
        "project_id": task.project_id,
        "is_completed": task.is_completed
    }


def get_tasks_from_todoist(project_id: Optional[str] = None, priority: Optional[int] = None) -> List[dict]:
    """Get tasks and return list of task data."""
    if not todoist_client:
        initialize_todoist_client()
    
    if project_id:
        tasks_paginator = todoist_client.get_tasks(project_id=project_id)
    else:
        tasks_paginator = todoist_client.get_tasks()
    
    tasks_list = []
    for page in tasks_paginator:
        for task in page:
            if task.is_completed:
                continue
            if priority and task.priority != priority:
                continue
                
            tasks_list.append({
                "id": task.id,
                "content": task.content,
                "description": task.description,
                "priority": task.priority,
                "project_id": task.project_id,
                "is_completed": task.is_completed
            })
    
    return tasks_list


def update_task_in_todoist(task_id: str, content: Optional[str] = None, 
                          description: Optional[str] = None, priority: Optional[int] = None) -> dict:
    """Update a task and return its new data."""
    if not todoist_client:
        initialize_todoist_client()
    
    task = todoist_client.update_task(
        task_id=task_id,
        content=content,
        description=description,
        priority=priority
    )
    
    return {
        "id": task.id,
        "content": task.content,
        "description": task.description,
        "priority": task.priority,
        "project_id": task.project_id,
        "is_completed": task.is_completed
    }


def delete_task_in_todoist(task_id: str) -> str:
    """Delete a task."""
    if not todoist_client:
        initialize_todoist_client()
    
    task = todoist_client.get_task(task_id=task_id)
    task_content = task.content
    todoist_client.delete_task(task_id=task_id)
    return f"Deleted: {task_content}"


def complete_task_in_todoist(task_id: str) -> str:
    """Complete a task."""
    if not todoist_client:
        initialize_todoist_client()
    
    task = todoist_client.get_task(task_id=task_id)
    task_content = task.content
    todoist_client.complete_task(task_id=task_id)
    return f"Completed: {task_content}"


def find_task_by_name(task_name: str) -> Optional[dict]:
    """Find a task by searching its content."""
    if not todoist_client:
        initialize_todoist_client()
    
    tasks_paginator = todoist_client.get_tasks()
    task_name_lower = task_name.lower()
    
    for page in tasks_paginator:
        for task in page:
            if not task.is_completed and task_name_lower in task.content.lower():
                return {
                    "id": task.id,
                    "content": task.content,
                    "description": task.description,
                    "priority": task.priority,
                    "project_id": task.project_id,
                    "is_completed": task.is_completed
                }
    return None


def get_projects_from_todoist() -> List[dict]:
    """Get all projects."""
    if not todoist_client:
        initialize_todoist_client()
    
    projects_paginator = todoist_client.get_projects()
    projects_list = []
    
    for page in projects_paginator:
        for project in page:
            projects_list.append({
                "id": project.id,
                "name": project.name,
                "is_shared": project.is_shared,
                "is_favorite": project.is_favorite
            })
    
    return projects_list
```

### 🔑 Key Concepts:

1. **One Global Client**: Create one `todoist_client` and reuse it
2. **Simple Returns**: Functions return `dict` or `str` directly
3. **No Complex Error Handling**: Let exceptions bubble up
4. **Essential Data Only**: Return only the important fields

---

## 🛠️ Step 3: Build Simple Utils (`utils.py`)

Just 3 tiny validation functions:

```python
"""
Simple Utility Functions
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("TODOIST_API_TOKEN")


def validate_api_token() -> bool:
    """Check if API token exists."""
    return API_TOKEN is not None


def validate_priority(priority: Optional[int]) -> int:
    """Make sure priority is between 1-4."""
    if priority is None:
        return 1
    return max(1, min(4, priority))


def validate_task_content(content: str) -> bool:
    """Check if task content is valid."""
    if not content or not content.strip():
        return False
    if len(content.strip()) > 500:
        return False
    return True
```

That's it! No complex formatting, no fancy summaries. Keep it simple.

---

## 🎛️ Step 4: Build the FastMCP Server (`main.py`)

FastMCP makes building MCP servers super easy with decorators:

```python
"""
Simple Todoist MCP Server

This server connects AI assistants to Todoist to manage tasks.
"""
from typing import Optional
from mcp.server.fastmcp import FastMCP
from apis import (
    create_task_in_todoist, 
    get_tasks_from_todoist, 
    update_task_in_todoist,
    delete_task_in_todoist,
    complete_task_in_todoist,
    find_task_by_name,
    get_projects_from_todoist
)
from utils import validate_api_token, validate_priority, validate_task_content

# Create MCP server
mcp = FastMCP("todoist-mcp")


@mcp.tool()
def create_task(content: str, description: Optional[str] = None, due_string: Optional[str] = None, priority: Optional[int] = None) -> str:
    """Create a new task in Todoist"""
    if not validate_api_token():
        return "Error: TODOIST_API_TOKEN not set"
    
    if not validate_task_content(content):
        return "Error: Invalid task content"
    
    priority = validate_priority(priority)
    task_data = create_task_in_todoist(content, description, due_string, priority)
    return f"Task created: {task_data}"


@mcp.tool()
def get_tasks(project_id: Optional[str] = None, priority: Optional[int] = None) -> str:
    """Get tasks from Todoist"""
    if not validate_api_token():
        return "Error: TODOIST_API_TOKEN not set"
    
    tasks_data = get_tasks_from_todoist(project_id, priority)
    return f"Tasks: {tasks_data}"


@mcp.tool()
def update_task(task_id: str, content: Optional[str] = None, description: Optional[str] = None, priority: Optional[int] = None) -> str:
    """Update an existing task"""
    if not validate_api_token():
        return "Error: TODOIST_API_TOKEN not set"
    
    if not task_id.strip():
        return "Error: Task ID required"
    
    task_data = update_task_in_todoist(task_id, content, description, priority)
    return f"Task updated: {task_data}"


@mcp.tool()
def delete_task(task_id: str) -> str:
    """Delete a task"""
    if not validate_api_token():
        return "Error: TODOIST_API_TOKEN not set"
    
    if not task_id.strip():
        return "Error: Task ID required"
    
    message = delete_task_in_todoist(task_id)
    return message


@mcp.tool()
def complete_task(task_id: str) -> str:
    """Mark task as completed"""
    if not validate_api_token():
        return "Error: TODOIST_API_TOKEN not set"
    
    if not task_id.strip():
        return "Error: Task ID required"
    
    message = complete_task_in_todoist(task_id)
    return message


@mcp.tool()
def find_task(task_name: str) -> str:
    """Find task by searching content"""
    if not validate_api_token():
        return "Error: TODOIST_API_TOKEN not set"
    
    if not task_name.strip():
        return "Error: Task name required"
    
    task_data = find_task_by_name(task_name)
    if task_data:
        return f"Found task: {task_data}"
    else:
        return "Task not found"


@mcp.tool()
def get_projects() -> str:
    """Get all projects from Todoist"""
    if not validate_api_token():
        return "Error: TODOIST_API_TOKEN not set"
    
    projects_data = get_projects_from_todoist()
    return f"Projects: {projects_data}"


if __name__ == "__main__":
    mcp.run()
```

### 🔑 FastMCP Magic:

1. **`@mcp.tool()` Decorator**: Each function becomes a tool automatically
2. **Automatic Schema Generation**: FastMCP creates tool schemas from function signatures
3. **Simple Returns**: Just return strings - FastMCP handles the rest
4. **Type Hints**: Function parameters become tool parameters automatically

---

## ⚙️ Step 5: Configuration

### `pyproject.toml`
```toml
[project]
name = "todoist-mcp-server"
version = "0.1.0"
description = "Simple Todoist MCP Server for Claude Desktop"
requires-python = ">=3.11"
dependencies = [
    "mcp[cli]",
    "todoist-api-python",
    "python-dotenv",
]
```

---

## 🔌 Step 6: Connect to Claude Desktop

### Update Claude Desktop Config

Edit your config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "todoist-mcp-server": {
      "command": "uv",
      "args": ["run", "/full/path/to/your/project/main.py"]
    }
  }
}
```

**💡 Tip**: Use full absolute paths to avoid issues!

---

## 🧪 Step 7: Test Everything

### Test Server Locally
```bash
uv run mcp dev main.py
```

You should see the server start without errors.

### Test with Claude Desktop

1. **Restart Claude Desktop completely**
2. **Start a new conversation**
3. **Try these commands**:

```
"Create a task called 'Test my MCP server' due tomorrow"
"Show me my current tasks"
"Complete the test task"
```

---

## 🎨 Step 8: Adding Your Own Tools

Want to add a new tool? Super easy with FastMCP!

1. **Add API function** to `apis.py`:
```python
def get_completed_tasks() -> List[dict]:
    # Your implementation
    pass
```

2. **Add tool** to `main.py`:
```python
@mcp.tool()
def get_completed_tasks() -> str:
    """Get all completed tasks"""
    if not validate_api_token():
        return "Error: TODOIST_API_TOKEN not set"
    
    tasks = get_completed_tasks()
    return f"Completed tasks: {tasks}"
```

That's it! FastMCP handles everything else automatically.

---

## 🏆 What You've Learned

### ✅ FastMCP Benefits
- **Super Simple**: Just add `@mcp.tool()` to any function
- **Automatic**: Schemas, routing, and parameter handling are automatic
- **Type-Safe**: Uses Python type hints for everything
- **Beginner-Friendly**: No complex patterns or abstractions

### ✅ Clean Code Principles
- **One file, one purpose**: Clear separation of concerns
- **Minimal error handling**: Only validate what's essential
- **Simple data structures**: Use basic Python types
- **No over-engineering**: Build exactly what you need

### ✅ Real Integration Skills
- **API Integration**: Connect to any REST API
- **Error Handling**: Basic validation and error messages
- **Configuration**: Environment variables and project setup
- **Testing**: Local and integration testing

---

## 🚀 Next Steps

### Easy Extensions
- **Labels**: Add label management to tasks
- **Due Dates**: Better due date handling and parsing
- **Recurring Tasks**: Handle recurring task patterns
- **Search**: More advanced task search features

### Other APIs You Could Connect
- **Google Calendar**: Sync tasks with calendar events
- **Slack**: Send notifications or create tasks from Slack
- **GitHub**: Create tasks from GitHub issues
- **Email**: Create tasks from emails

### Learning More
- **FastMCP Docs**: Learn more advanced FastMCP features
- **Todoist API**: Explore more Todoist capabilities
- **MCP Protocol**: Understand the underlying protocol

---

## 📝 Summary

You built a complete MCP server in less than 200 lines of code that:

✅ **Connects Claude to Todoist** with 7 useful tools  
✅ **Uses modern FastMCP** for simplicity  
✅ **Follows clean code principles** with clear structure  
✅ **Is easily extensible** for new features  
✅ **Works reliably** with proper validation  

**Most importantly**: You now understand how to build AI integrations with any API using MCP!

---

## 🤝 Contributing

Want to improve this guide or add features?

1. Fork the repository
2. Make your changes  
3. Test everything works
4. Submit a pull request

Keep the code simple and beginner-friendly!

---

**Happy building! 🎉**

*The best way to learn is by doing. Start with this simple server, then extend it with your own ideas!*
