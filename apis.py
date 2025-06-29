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
    
    task : Task = todoist_client.add_task(
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