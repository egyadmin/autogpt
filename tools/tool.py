"""
تمثيل للمهام التي ينفذها الوكيل
"""
import uuid
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime

class TaskStatus(str, Enum):
    """حالات المهمة المحتملة"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"

class Task:
    """تمثيل للمهمة التي سيتم تنفيذها بواسطة الوكيل"""
    
    def __init__(
        self, 
        name: str, 
        description: str, 
        agent_id: Optional[str] = None,
        status: TaskStatus = TaskStatus.PENDING,
        task_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        priority: int = 5,  # إضافة معلمة priority بقيمة افتراضية 5
        tags: Optional[List[str]] = None  # إضافة معلمة tags
    ):
        self.id = task_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.status = status
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        self.completed_at = None
        self.agent_id = agent_id
        self.parent_id = parent_id
        self.priority = priority  # تخزين الأولوية
        self.tags = tags or []  # تخزين الوسوم
        self.result = None
        self.error_message = None
        self.subtasks: List[Task] = []
        self.feedback: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
    
    def add_subtask(self, name: str, description: str, priority: int = 5) -> 'Task':
        """إضافة مهمة فرعية لهذه المهمة"""
        subtask = Task(
            name=name, 
            description=description, 
            agent_id=self.agent_id,
            parent_id=self.id,
            priority=priority
        )
        self.subtasks.append(subtask)
        self.updated_at = datetime.now()
        return subtask
    
    def update_status(self, status: TaskStatus) -> None:
        """تحديث حالة المهمة"""
        self.status = status
        self.updated_at = datetime.now()
        if status == TaskStatus.COMPLETED or status == TaskStatus.FAILED:
            self.completed_at = self.updated_at
    
    def complete(self, result: Any) -> None:
        """تحديث المهمة كمكتملة مع النتيجة"""
        self.result = result
        self.update_status(TaskStatus.COMPLETED)
    
    def fail(self, error_message: str) -> None:
        """تحديث المهمة كفاشلة مع سبب الفشل"""
        self.error_message = error_message
        self.update_status(TaskStatus.FAILED)
    
    def cancel(self) -> None:
        """إلغاء المهمة"""
        self.update_status(TaskStatus.CANCELED)
    
    def add_feedback(self, user_id: str, rating: int, comment: Optional[str] = None) -> None:
        """إضافة تقييم المستخدم للمهمة"""
        self.feedback[user_id] = {
            "rating": rating,  # 1-5 نجوم
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        }
        self.updated_at = datetime.now()
    
    def add_metadata(self, key: str, value: Any) -> None:
        """إضافة بيانات وصفية إضافية للمهمة"""
        self.metadata[key] = value
        self.updated_at = datetime.now()
    
    def to_dict(self, include_subtasks: bool = True) -> Dict[str, Any]:
        """تحويل المهمة إلى قاموس لعرضها أو تخزينها"""
        result = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "agent_id": self.agent_id,
            "parent_id": self.parent_id,
            "priority": self.priority,
            "tags": self.tags,
            "result": self.result,
            "error_message": self.error_message,
            "feedback": self.feedback,
            "metadata": self.metadata,
        }
        
        if include_subtasks:
            result["subtasks"] = [subtask.to_dict(include_subtasks) for subtask in self.subtasks]
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """إنشاء مهمة من قاموس"""
        task = cls(
            name=data["name"],
            description=data["description"],
            agent_id=data.get("agent_id"),
            status=TaskStatus(data["status"]),
            task_id=data["id"],
            parent_id=data.get("parent_id"),
            priority=data.get("priority", 5),
            tags=data.get("tags", [])
        )
        
        # تحويل التواريخ من النص إلى كائنات datetime
        if "created_at" in data:
            task.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            task.updated_at = datetime.fromisoformat(data["updated_at"])
        if "completed_at" in data and data["completed_at"]:
            task.completed_at = datetime.fromisoformat(data["completed_at"])
            
        task.result = data.get("result")
        task.error_message = data.get("error_message")
        task.feedback = data.get("feedback", {})
        task.metadata = data.get("metadata", {})
        
        # إضافة المهام الفرعية إذا كانت موجودة
        if "subtasks" in data:
            for subtask_data in data["subtasks"]:
                subtask = Task.from_dict(subtask_data)
                task.subtasks.append(subtask)
                
        return task