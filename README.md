# Building a Todoist MCP Server from Scratch: Complete DIY Guide

A complete step-by-step tutorial for absolute beginners to build their first MCP (Model Context Protocol) server that connects Claude Desktop to Todoist. No prior MCP knowledge required!

## 🎯 What is MCP and What You'll Build

**MCP (Model Context Protocol)** is a way for AI assistants like Claude to connect to external services and tools. Think of it as a bridge that lets Claude talk to your favorite apps.

**What you'll build**: A server that gives Claude these superpowers with your Todoist account:
- ✅ **Create tasks** with descriptions, due dates, and priorities
- 📋 **Get and filter tasks** from your projects
- ✏️ **Update existing tasks** 
- ✅ **Mark tasks as complete**
- 🗑️ **Delete tasks**
- 🔍 **Filter tasks** using Todoist's powerful query language
- 📁 **List all projects**

**Why this is awesome**: Claude can now help you manage your todo list naturally through conversation!

## 🛠️ Prerequisites

Before we start, you'll need:

1. **Python 3.11+** installed on your computer
2. **A Todoist account** (the free version works perfectly)
3. **UV package manager** (we'll install this)
4. **Claude Desktop app** installed
5. **A code editor** (VS Code, Cursor, or any text editor)

## 📋 Step 1: Project Setup

### 1.1 Install UV Package Manager

UV is a fast Python package manager. Install it:

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.sh | iex"
```

### 1.2 Create Your Project

```bash
# Create a new directory
mkdir todoist-mcp-server
cd todoist-mcp-server

# Initialize the project
uv init
```

### 1.3 Install Required Packages

```bash
# Install all the packages we'll need
uv add "mcp[cli]"           # The MCP framework
uv add "todoist-api-python" # Todoist's official Python SDK
uv add "python-dotenv"      # For environment variables
uv add tzdata               # For windows
```

**What these packages do**:
- `mcp[cli]`: The MCP framework that handles the communication protocol
- `todoist-api-python`: Official Todoist SDK for making API calls
- `python-dotenv`: Loads environment variables from a .env file

### 1.4 Get Your Todoist API Token

1. Go to [Todoist Settings → Integrations](https://todoist.com/prefs/integrations)
2. Scroll down to "API token"
3. Copy your API token
4. **Optional**: Create a `.env` file in your project directory:

```bash
# .env
TODOIST_API_TOKEN=your_actual_token_here
```

⚠️ **Important**: Replace `your_actual_token_here` with your real token!

**Note**: You can either use this .env file OR include the token directly in your Claude Desktop config later (recommended for simplicity).

## 🔧 Step 2: Building the API Layer (`apis.py`)

This file will handle all communication with Todoist. We'll build it function by function.

### 2.1 Create the File and Basic Setup

Create `apis.py` and start with the imports:

```python
"""
Simple Todoist API Functions

This file contains all the functions that talk to Todoist's API.
Each function does one specific thing with your tasks.
"""

from datetime import date
import os
from typing import List, Optional
from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
API_TOKEN = os.getenv("TODOIST_API_TOKEN")
todoist_client: Optional[TodoistAPI] = None
```

**What this sets up**: Imports the Todoist SDK, loads your API token from the .env file, and creates a global variable to store the client connection. This is the foundation for all our API calls.

### 2.2 Create the Client Connection Function

Add this function to manage the connection to Todoist:

```python
def _get_todoist_client() -> TodoistAPI:
    """Get the initialized Todoist client, initializing it if necessary."""
    global todoist_client
    if todoist_client is None:
        if not API_TOKEN:
            raise Exception("TODOIST_API_TOKEN not set")
        todoist_client = TodoistAPI(API_TOKEN)
    return todoist_client
```

**What this does**: Creates a single Todoist client connection that gets reused across all API calls. This is more efficient than creating a new connection every time.

### 2.3 Function 1: Get Projects

Add the projects function:

```python
def get_projects_from_todoist() -> List[dict]:
    """Get all projects."""
    client = _get_todoist_client()
    
    projects_paginator = client.get_projects()
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

**What this does**: Retrieves all your Todoist projects and returns them as a list of dictionaries with project ID, name, and sharing/favorite status.

### 2.4 Function 2: Get Tasks

Add the function to retrieve tasks:

```python
def get_tasks_from_todoist(project_id: Optional[str] = None, priority: Optional[int] = None) -> List[dict]:
    """Get tasks and return list of task data."""
    client = _get_todoist_client()
    
    if project_id:
        tasks_paginator = client.get_tasks(project_id=project_id)
    else:
        tasks_paginator = client.get_tasks()
    
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
                "labels": task.labels,
                "due": task.due,
                "completed_at": task.completed_at,
                "deadline": task.deadline,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "url": task.url,
                "description": task.description,
                "priority": task.priority,
                "project_id": task.project_id,
                "is_completed": task.is_completed
            })
    
    return tasks_list
```

**What this does**: Retrieves all incomplete tasks from Todoist, with optional filtering by project or priority. Handles Todoist's pagination automatically and returns a clean list of task dictionaries.

### 2.5 Function 3: Filter Tasks

Add the task filtering function that uses Todoist's powerful query language:

**What is Todoist Query Language?**
Todoist has a built-in query system that lets you filter tasks using natural expressions like `"today"`, `"p1"`, `"overdue"`, or `"@shopping"`. This is much more powerful than simple text search!

```python
def filter_tasks_in_todoist(query: str) -> Optional[dict]:
    """Find tasks using Todoist's query language."""
    client = _get_todoist_client()
    
    tasks_paginator = client.filter_tasks(query=query)
    
    for page in tasks_paginator:
        for task in page:
            return {
                "id": task.id,
                "content": task.content,
                "description": task.description,
                "priority": task.priority,
                "project_id": task.project_id,
                "is_completed": task.is_completed
            }
    return None
```

**What this does**: Uses Todoist's powerful query language to find tasks matching specific criteria like `"today"`, `"p1"`, `"overdue"`, or `"@shopping"`. Returns the first matching task or None if no matches found.

**Example Todoist queries**:
- `"today"` - Tasks due today
- `"tomorrow"` - Tasks due tomorrow
- `"p1"` - Priority 1 (urgent) tasks
- `"p4"` - Priority 4 (low) tasks
- `"overdue"` - Overdue tasks
- `"no date"` - Tasks without due dates
- `"@shopping"` - Tasks with shopping label
- `"#work"` - Tasks in work project
- `"assigned by: me"` - Tasks you assigned to others
- `"created: today"` - Tasks created today
- `"today & p1"` - Tasks due today AND priority 1

### 2.6 Function 4: Create Tasks

Add the task creation function:

```python
def create_task_in_todoist(content: str, description: Optional[str] = None, 
                          due_date: Optional[date] = None, priority: Optional[int] = None, 
                          project_id: Optional[str] = None, labels: Optional[List[str]] = None) -> dict:
    """Create a new task and return its data."""
    client = _get_todoist_client()
    
    task: Task = client.add_task(
        content=content,
        description=description,
        due_date=due_date,
        project_id=project_id,
        priority=priority,
        labels=labels
    )
    
    return {
        "id": task.id,
        "content": task.content,
        "description": task.description,
        "priority": task.priority,
        "project_id": task.project_id,
        "is_completed": task.is_completed
    }
```

**What this does**: Creates a new task in Todoist with all the optional parameters (description, due date, priority, project, labels). Returns the created task's information as a dictionary.

### 2.7 Function 5: Update Tasks

Add the task update function:

```python
def update_task_in_todoist(task_id: str, content: Optional[str] = None, 
                          description: Optional[str] = None, priority: Optional[int] = None, 
                          due_date: Optional[date] = None) -> dict:
    """Update a task and return its new data."""
    client = _get_todoist_client()
    
    task = client.update_task(
        task_id=task_id,
        due_date=due_date,
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
```

**What this does**: Updates an existing task with new information (content, description, priority, due date). Only the fields you provide will be changed, others remain unchanged.

### 2.8 Function 6: Delete Tasks

Add the task deletion function:

```python
def delete_task_in_todoist(task_id: str) -> str:
    """Delete a task."""
    client = _get_todoist_client()
    
    task = client.get_task(task_id=task_id)
    task_content = task.content
    client.delete_task(task_id=task_id)
    return f"Deleted: {task_content}"
```

**What this does**: Permanently deletes a task from Todoist. Gets the task name first so it can return a confirmation message with the deleted task's title.

### 2.9 Function 7: Complete Tasks

Add the task completion function:

```python
def complete_task_in_todoist(task_id: str) -> str:
    """Complete a task."""
    client = _get_todoist_client()
    
    task = client.get_task(task_id=task_id)
    task_content = task.content
    client.complete_task(task_id=task_id)
    return f"Completed: {task_content}"
```

**What this does**: Marks a task as completed in Todoist. The task stays in your account but is marked as done, unlike delete which removes it permanently.

## 🎛️ Step 3: Building the MCP Server (`main.py`)

Now we'll create the MCP server that exposes these functions as tools for Claude.

### 3.1 Create the File and Basic Setup

Create `main.py` and start with imports:

```python
"""
Simple Todoist MCP Server

This server connects AI assistants to Todoist to manage tasks.
"""
from datetime import date
import os
from typing import List, Optional
from mcp.server.fastmcp import FastMCP
from apis import (
    get_projects_from_todoist,
    get_tasks_from_todoist, 
    filter_tasks_in_todoist,
    create_task_in_todoist, 
    update_task_in_todoist,
    delete_task_in_todoist,
    complete_task_in_todoist
)

# Create MCP server
mcp = FastMCP("todoist-mcp")
```

**What this sets up**: Imports the MCP framework and all our API functions, then creates the MCP server instance that will expose our tools to Claude.

### 3.2 Helper Function for Reading Files

Add this helper function:

```python
def read_file(filename: str) -> str:
    """Read content from a file."""
    folder_path = "/Users/chaitanya.anand/Desktop/Projects/Atlan/fifth-elephant-mcp-workshop/"
    try:
        with open(folder_path + filename, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return f"Error: file '{filename}' not found."
    except Exception as e:
        return f"Error reading file '{filename}': {str(e)}"
```

**What this does**: A simple helper function to read files with basic error handling. We'll use this later for prompt templates and resources.

### 3.3 Tool 1: Get Projects

Add the get projects tool:

```python
@mcp.tool()
def get_projects() -> str:
    """Get all projects from Todoist"""
    
    projects_data = get_projects_from_todoist()
    return f"Projects: {projects_data}"
```

**What this does**: The `@mcp.tool()` decorator exposes this function as a tool that Claude can use. Function parameters become tool parameters, and the docstring becomes the tool description.

### 3.4 Tool 2: Get Tasks

Add the get tasks tool:

```python
@mcp.tool()
def get_tasks(project_id: Optional[str] = None, priority: Optional[int] = None) -> str:
    """Get tasks from Todoist"""
    
    tasks_data = get_tasks_from_todoist(project_id, priority)
    return f"Tasks: {tasks_data}"
```

**What this does**: Exposes the get_tasks API function as an MCP tool. Claude can call this to retrieve tasks with optional filtering.

### 3.5 Tool 3: Create Task

Add the create task tool:

```python
@mcp.tool()
def create_task(content: str, description: Optional[str] = None, 
               due_date: Optional[date] = None, priority: Optional[int] = None, 
               project_id: Optional[str] = None, labels: Optional[List[str]] = None) -> str:
    """Create a new task in Todoist"""
    task_data = create_task_in_todoist(content, description, due_date, priority, project_id, labels)
    return f"Task created: {task_data}"
```

### 3.6 Tool 4: Filter Tasks

Add the filter tasks tool:

```python
@mcp.tool()
def filter_tasks(query: str) -> str:
    """Find tasks using Todoist query language"""
    
    task_data = filter_tasks_in_todoist(query)
    if task_data:
        return f"Found task(s): {task_data}"
    else:
        return "Task not found"
```

**What makes this powerful**: Uses Todoist's query language to filter by due dates, priorities, projects, and labels. Much more flexible than simple text search.

### 3.7 Tool 5: Update Task

Add the update task tool:

```python
@mcp.tool()
def update_task(task_id: str, content: Optional[str] = None, 
               description: Optional[str] = None, due_date: Optional[date] = None, 
               priority: Optional[int] = None) -> str:
    """Update an existing task"""
    
    task_data = update_task_in_todoist(task_id, content, description, priority, due_date)
    return f"Task updated: {task_data}"
```

### 3.8 Tool 6: Delete Task

Add the delete task tool:

```python
@mcp.tool()
def delete_task(task_id: str) -> str:
    """Delete a task"""
    
    message = delete_task_in_todoist(task_id)
    return message
```

### 3.9 Tool 7: Complete Task

Add the complete task tool:

```python
@mcp.tool()
def complete_task(task_id: str) -> str:
    """Mark task as completed"""
    
    message = complete_task_in_todoist(task_id)
    return message
```

### 3.10 Adding Resources (Optional but Cool)

Add these resource functions for extra functionality:

```python
@mcp.resource("stats://productivity_stats")
def get_productivity_stats() -> str:
    """Get productivity statistics and work patterns."""
    return read_file("/Users/chaitanya.anand/Desktop/Projects/Atlan/fifth-elephant-mcp-workshop/resources/productivity_stats.json")

@mcp.resource("file://documents/{name}")
def read_document(name: str) -> str:
    """Read a document by name."""
    return f"Content of {name}"

@mcp.resource("knowledgebase://bapple_knowledgebase")
def get_bapple_knowledgebase() -> str:
    """Get bapple knowledgebase."""
    return read_file("/Users/chaitanya.anand/Desktop/Projects/Atlan/fifth-elephant-mcp-workshop/resources/bapple_knowledgebase.md")
```

### 3.11 Adding Prompts (Optional but Cool)

Add these prompt functions:

```python
@mcp.prompt()
def project_planning_assistant(task_description: str, project_name: Optional[str] = None) -> str:
    """Generate a comprehensive project plan with task breakdown and optimization strategies"""
    prompt_template = read_file("/Users/chaitanya.anand/Desktop/Projects/Atlan/fifth-elephant-mcp-workshop/prompts/project_planning_assistant.txt")
    return prompt_template.format(
        task_description=task_description,
        project_name=project_name or "None"
    )

@mcp.prompt()
def project_time_optimization_analyzer(project_name: Optional[str] = None, project_id: Optional[str] = None) -> str:
    """Analyze project workload and provide time optimization recommendations"""
    project_info = f"project_name: {project_name}" if project_name else f"project_id: {project_id}" if project_id else "all projects"
    
    prompt_template = read_file("/Users/chaitanya.anand/Desktop/Projects/Atlan/fifth-elephant-mcp-workshop/prompts/project_time_optimization_analyzer.txt")
    return prompt_template.format(
        project_name=project_name or "None",
        project_id=project_id or "None",
        project_info=project_info
    )
```

### 3.12 Start the Server

Add the server startup code:

```python
if __name__ == "__main__":
    mcp.run()
```

**What this does**: Starts the MCP server when you run the script directly.

## ⚙️ Step 4: Configuration

### 4.1 Create `pyproject.toml`

Create this file to define your project dependencies:

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

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### 4.2 Your Final File Structure

Your project should now look like this:

```
todoist-mcp-server/
├── main.py              # MCP server with tools
├── apis.py              # Todoist API functions
├── .env                 # Your API token (keep secret!)
├── pyproject.toml       # Project configuration
├── uv.lock             # Dependency lock file
├── prompts/            # Optional: prompt templates
└── resources/          # Optional: additional resources
```

## 🧪 Step 5: Testing Your Server

### 5.1 Test the Server Locally

First, let's make sure your server starts without errors:

```bash
# Make sure you're in your project directory
cd todoist-mcp-server

# Run the server in development mode
uv run mcp dev main.py
```

**What should happen**:
- ✅ No error messages
- ✅ Server starts and shows available tools
- ✅ You should see your 7 tools listed

**If you see errors**:
- Check your `.env` file has the correct API token
- Make sure all imports are correct
- Verify your Todoist API token is valid


## 🔌 Step 6: Connect to Claude Desktop

### 6.1 Find Your Claude Desktop Config

The config file location depends on your OS:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

### 6.2 Get Your Full Project Path

Find your project's absolute path:

```bash
# In your project directory
pwd
```

Find the exact path for your python binary in the virtual environment:
```bash
# This will show the path to your virtual environment's python
uv run which python
```

**Why the virtual environment path?** Using the virtual environment's python ensures Claude uses the correct Python installation with all your project dependencies installed.

Copy both these paths - you'll need them for the config.

### 6.3 Update Claude Desktop Config

Edit the config file and add your MCP server:

```json
{
  "mcpServers": {
    "todoist-mcp-server": {
      "command": "/FULL/PATH/TO/YOUR/VENV/bin/python",
      "args": ["/FULL/PATH/TO/YOUR/PROJECT/main.py"],
      "env": {
        "TODOIST_API_TOKEN": "your_actual_todoist_token_here"
      }
    }
  }
}
```

**Important**: 
- Replace `/FULL/PATH/TO/YOUR/VENV/bin/python` with your virtual environment's python path
- Replace `/FULL/PATH/TO/YOUR/PROJECT/main.py` with your project's main.py path
- Replace `your_actual_todoist_token_here` with your real Todoist API token
- Use forward slashes even on Windows
- Make sure all paths are absolute, not relative

**Example**:
```json
{
  "mcpServers": {
    "todoist-mcp-server": {
      "command": "/Users/yourname/todoist-mcp-server/.venv/bin/python",
      "args": ["/Users/yourname/todoist-mcp-server/main.py"],
      "env": {
        "TODOIST_API_TOKEN": "894f574fcd8fdfbce3123459de09dce4cc7ad06"
      }
    }
  }
}
```

**Two ways to handle environment variables:**

**Option 1: Direct in config (Recommended)**
Include the `env` section in your Claude config as shown above. This is simpler and eliminates the need for a separate .env file.

**Option 2: Use .env file**
If you prefer using a .env file, you can omit the `env` section from the config and the server will automatically load from your .env file.


### 6.4 Restart Claude Desktop

1. **Completely quit Claude Desktop** (not just close the window)
2. **Wait 5 seconds**
3. **Restart Claude Desktop**
4. **Start a new conversation**

## 🎉 Step 7: Test with Claude

### 7.1 Basic Test

In a new Claude conversation, try:

```
"Can you help me create a task in Todoist called 'Test my MCP server'?"
```

**What should happen**:
- Claude should respond that it can help with Todoist
- A new task should appear in your Todoist
- Claude should confirm the task was created

### 7.2 More Tests

Try these commands:

```
"What projects do I have in Todoist?"
"Show me all my current tasks"
"Filter tasks using the query 'today'"
"Filter tasks with priority 1 using query 'p1'"
"Filter overdue tasks using query 'overdue'"
"Create a task 'Buy groceries' due tomorrow with high priority"
"Update the groceries task to change priority to 1"
"Mark the groceries task as complete"
```

### 7.3 If Something Goes Wrong

**Common issues and fixes**:

1. **"I don't see any MCP tools"**
   - Check Claude config file syntax (use a JSON validator)
   - Verify the file path is correct and absolute
   - Make sure you restarted Claude completely

2. **"API token not set" error**
   - If using Claude config `env` section: Check your token is correct in the config
   - If using .env file: Check your `.env` file exists and verify the token is correct (no extra spaces)
   - Make sure the token has no extra quotes or spaces around it

3. **"Module not found" error**
   - Run `uv sync` to install dependencies
   - Check that all imports in your files are correct

4. **Tasks not appearing in Todoist**
   - Verify your API token has the right permissions
   - Check if tasks are in a different project
   - Look for error messages in Claude's response

## 🔧 Step 8: Troubleshooting Guide

### 8.1 Debug Mode

Run your server in debug mode to see detailed logs:

```bash
uv run mcp dev main.py --debug
```

### 8.2 Check Claude's Logs

On macOS, Claude's logs are in:
```
~/Library/Logs/Claude/
```

Look for error messages about your MCP server.

### 8.3 Common Error Solutions

**ImportError: No module named 'mcp'**
```bash
uv add "mcp[cli]"
```

**ImportError: No module named 'todoist_api_python'**
```bash
uv add "todoist-api-python"
```

**API token not set**
- Check your `.env` file exists
- Verify the token is on the correct line
- Make sure there are no extra spaces

**Claude doesn't see the tools**
- Verify JSON syntax in Claude config (use a JSON validator)
- Use absolute paths, not relative
- Make sure you're using the virtual environment's python path (not system python)
- Restart Claude completely

**Wrong Python or missing dependencies**
- Verify you're using the `.venv/bin/python` path from your project
- Run `uv run which python` to confirm the correct path
- Make sure your virtual environment has all dependencies installed

## 🚀 Step 9: What You've Built

Congratulations! You've built a complete MCP server that:

✅ **Connects Claude to Todoist** with 7 powerful tools
✅ **Handles all basic task management** (create, read, update, delete, complete)
✅ **Supports advanced features** like search, projects, and filtering
✅ **Uses modern Python patterns** with type hints and clean code
✅ **Is easily extensible** for new features
✅ **Follows MCP best practices** with proper error handling

## 🎯 Step 10: What's Next?

### 10.1 Easy Extensions

Add these features to make your server even better:

**Labels Management**:
```python
@mcp.tool()
def add_label_to_task(task_id: str, label: str) -> str:
    """Add a label to a task"""
    # Implementation here
```

**Due Date Parsing**:
```python
@mcp.tool()
def create_task_with_natural_due_date(content: str, due_string: str) -> str:
    """Create task with natural language due date like 'tomorrow' or 'next Monday'"""
    # Implementation here
```

**Task Comments**:
```python
@mcp.tool()
def add_comment_to_task(task_id: str, comment: str) -> str:
    """Add a comment to a task"""
    # Implementation here
```

### 10.2 Connect Other Services

Now that you understand MCP, you can connect Claude to:

- **Google Calendar**: Sync tasks with calendar events
- **Slack**: Create tasks from Slack messages
- **GitHub**: Turn issues into tasks
- **Email**: Create tasks from emails
- **Notion**: Sync with Notion databases

### 10.3 Advanced MCP Features

Explore these MCP capabilities:

- **Resources**: Provide Claude with knowledge bases
- **Prompts**: Create reusable prompt templates
- **Sampling**: Let Claude make API calls proactively
- **Servers**: Chain multiple MCP servers together

## 📚 Learn More

### Documentation
- [MCP Documentation](https://modelcontextprotocol.io/)
- [FastMCP Guide](https://github.com/jlowin/fastmcp)
- [Todoist API Docs](https://developer.todoist.com/rest/v2/)

### Community
- [MCP GitHub Discussions](https://github.com/modelcontextprotocol/python-sdk/discussions)
- [MCP Discord](https://discord.gg/modelcontextprotocol)

## 🎉 Summary

You've successfully built a complete MCP server from scratch! Here's what you accomplished:

1. **Learned MCP fundamentals** - Understanding the protocol and architecture
2. **Built a clean API layer** - Structured, testable functions for Todoist
3. **Created 7 powerful tools** - Everything Claude needs to manage tasks
4. **Configured Claude integration** - Connected your server to Claude Desktop
5. **Tested thoroughly** - Ensured everything works reliably
6. **Learned debugging** - How to troubleshoot and fix issues

**Most importantly**: You now have the skills to build MCP servers for any API or service. The pattern you learned here applies to connecting Claude to any external system.

**Keep building!** The MCP ecosystem is growing rapidly, and your skills will be valuable for creating amazing AI integrations.

---

**Happy coding! 🚀**

*Remember: The best way to learn is by building. Start with this server, then extend it with your own ideas and connect it to your favorite services!*
