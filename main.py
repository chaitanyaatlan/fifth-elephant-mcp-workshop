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