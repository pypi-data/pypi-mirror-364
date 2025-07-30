"""
Pydantic models for Taskflow SDK.
"""

from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime


class Params(BaseModel):
    """Parameters for task scheduling."""
    task_name: str
    task_args: Optional[List[Any]] = []
    task_kwargs: Optional[Dict[str, Any]] = {}
    schedule_time: Optional[datetime] = None
    callback_url: Optional[str] = None


class Notif(BaseModel):
    """Webhook notification data from Taskflow."""
    task_id: str
    task_name: str
    task_args: List[Any]
    task_kwargs: Dict[str, Any]
    schedule_time: Optional[str] = None
    status: str
    timestamp: str
    message: str 