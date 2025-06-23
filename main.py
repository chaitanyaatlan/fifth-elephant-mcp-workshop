"""
Simple Todoist MCP Server

This server connects AI assistants to Todoist to manage tasks.
"""
from datetime import date
import os
from typing import List, Optional
from mcp.server.fastmcp import FastMCP
from apis import (
    create_task_in_todoist, 
    get_tasks_from_todoist, 
    update_task_in_todoist,
    delete_task_in_todoist,
    complete_task_in_todoist,
    get_projects_from_todoist,
    filter_tasks_in_todoist
)

# Create MCP server
mcp = FastMCP("todoist-mcp")


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


@mcp.tool()
def create_task(content: str, description: Optional[str] = None, due_date: Optional[date] = None, priority: Optional[int] = None, project_id: Optional[str] = None, labels: Optional[List[str]] = None) -> str:
    """
    Create a new task in Todoist.
    
    Args:
        content: Task title (required)
        description: Optional task description
        due_date: Due date as Python date object
        priority: Priority level 1-4 (1=normal, 4=urgent)
        project_id: Project ID to add task to (default: Inbox)
        labels: List of label names to attach
    
    Returns:
        Success message with task details
    """
    task_data = create_task_in_todoist(content, description, due_date, priority, project_id, labels)
    return f"Task created: {task_data}"


@mcp.tool()
def get_tasks(project_id: Optional[str] = None, priority: Optional[int] = None) -> str:
    """
    Get tasks from Todoist (incomplete tasks only).
    
    Args:
        project_id: Filter by specific project ID
        priority: Filter by priority level (1-4)
    
    Returns:
        List of task details including ID, content, description, priority
    """
    
    tasks_data = get_tasks_from_todoist(project_id, priority)
    return f"Tasks: {tasks_data}"


@mcp.tool()
def update_task(task_id: str, content: Optional[str] = None, description: Optional[str] = None, due_date: Optional[date] = None, priority: Optional[int] = None) -> str:
    """Update an existing task"""
    
    task_data = update_task_in_todoist(task_id, content, description, priority, due_date)
    return f"Task updated: {task_data}"


@mcp.tool()
def delete_task(task_id: str) -> str:
    """Delete a task"""
    
    message = delete_task_in_todoist(task_id)
    return message


@mcp.tool()
def complete_task(task_id: str) -> str:
    """Mark task as completed"""
    
    message = complete_task_in_todoist(task_id)
    return message


@mcp.tool()
def filter_tasks(query: str) -> str:
    """Find task by writing a todoist query"""
    
    task_data = filter_tasks_in_todoist(query)
    if task_data:
        return f"Found task(s): {task_data}"
    else:
        return "Task not found"


@mcp.tool()
def get_projects() -> str:
    """
    Get all projects from Todoist account.
    
    Returns:
        List of projects with ID, name, shared status, and favorite status
    """
    
    projects_data = get_projects_from_todoist()
    return f"Projects: {projects_data}"


@mcp.resource("stats://productivity_stats")
def get_productivity_stats() -> str:
    """Get productivity statistics and work patterns."""
    return read_file("resources/productivity_stats.json")

@mcp.resource("file://documents/{name}")
def read_document(name: str) -> str:
    """Read a document by name."""
    # This would normally read from disk
    return f"Content of {name}"


@mcp.resource("knowledgebase://bapple_knowledgebase")
def get_bapple_knowledgebase() -> str:
    """Get bapple knowledgebase."""
    return read_file("resources/bapple_knowledgebase.md")

@mcp.resource("knowledgebase://filter_cheatsheet")
def get_filter_cheatsheet() -> str:
    """Get filter cheatsheet."""
    return read_file("resources/filters.csv")


@mcp.prompt()
def project_planning_assistant(task_description: str, project_name: Optional[str] = None) -> str:
    """Generate a comprehensive project plan with task breakdown and optimization strategies"""
    prompt_template = read_file("prompts/project_planning_assistant.txt")
    return prompt_template.format(
        task_description=task_description,
        project_name=project_name or "None"
    )


@mcp.prompt()
def project_time_optimization_analyzer(project_name: Optional[str] = None, project_id: Optional[str] = None) -> str:
    """Analyze project workload and provide time optimization recommendations"""
    project_info = f"project_name: {project_name}" if project_name else f"project_id: {project_id}" if project_id else "all projects"
    
    prompt_template = read_file("prompts/project_time_optimization_analyzer.txt")
    return prompt_template.format(
        project_name=project_name or "None",
        project_id=project_id or "None",
        project_info=project_info
    )


if __name__ == "__main__":
    mcp.run()