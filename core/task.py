# مثال مبسط لفئة Task
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"

class Task:
    def __init__(self, name, description, agent_id=None, status=TaskStatus.PENDING):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.status = status
        self.agent_id = agent_id
        self.subtasks = []
        self.result = None
        self.created_at = datetime.now()