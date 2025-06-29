"""
Simple Utility Functions
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API token from environment
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