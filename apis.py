"""
Simple Todoist API Functions
"""

from datetime import date
import os
from typing import List, Optional
from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("TODOIST_API_TOKEN")
todoist_client: Optional[TodoistAPI] = None


def _get_todoist_client() -> TodoistAPI:
    """Get the initialized Todoist client, initializing it if necessary."""
    global todoist_client
    if todoist_client is None:
        if not API_TOKEN:
            raise Exception("TODOIST_API_TOKEN not set")
        todoist_client = TodoistAPI(API_TOKEN)
    return todoist_client


def create_task_in_todoist(content: str, description: Optional[str] = None, due_date: Optional[date] = None, priority: Optional[int] = None, project_id: Optional[str] = None, labels: Optional[List[str]] = None) -> dict:
    """Create a new task and return its data."""
    client = _get_todoist_client()
    
    task : Task = client.add_task(
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
                "labels": task.labels,
                "due": task.due,
                "completed_at": task.completed_at,
                "deadline": task.deadline,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "url": task.url,
                "content": task.content,
                "description": task.description,
                "priority": task.priority,
                "project_id": task.project_id,
                "is_completed": task.is_completed
            })
    
    return tasks_list


def update_task_in_todoist(task_id: str, content: Optional[str] = None, 
                          description: Optional[str] = None, priority: Optional[int] = None, due_date: Optional[date] = None) -> dict:
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


def delete_task_in_todoist(task_id: str) -> str:
    """Delete a task."""
    client = _get_todoist_client()
    
    task = client.get_task(task_id=task_id)
    task_content = task.content
    client.delete_task(task_id=task_id)
    return f"Deleted: {task_content}"


def complete_task_in_todoist(task_id: str) -> str:
    """Complete a task."""
    client = _get_todoist_client()
    
    task = client.get_task(task_id=task_id)
    task_content = task.content
    client.complete_task(task_id=task_id)
    return f"Completed: {task_content}"


def filter_tasks_in_todoist(query: str) -> Optional[dict]:
    """Find a task by writing a todoist query."""
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