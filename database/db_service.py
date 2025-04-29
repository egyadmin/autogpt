"""
واجهة أساسية لخدمات قاعدة البيانات
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

from core.task import Task
from core.agent import Agent

class DatabaseService:
    """واجهة أساسية لخدمات قاعدة البيانات"""
    
    def save_agent(self, agent: Agent) -> None:
        """حفظ بيانات الوكيل"""
        raise NotImplementedError("This method should be implemented by subclasses")
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """استرجاع بيانات وكيل محدد"""
        raise NotImplementedError("This method should be implemented by subclasses")
    
    def get_all_agents(self, creator_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """استرجاع بيانات جميع الوكلاء"""
        raise NotImplementedError("This method should be implemented by subclasses")
    
    def delete_agent(self, agent_id: str) -> bool:
        """حذف وكيل من قاعدة البيانات"""
        raise NotImplementedError("This method should be implemented by subclasses")
    
    def save_task(self, task: Task) -> None:
        """حفظ بيانات المهمة"""
        raise NotImplementedError("This method should be implemented by subclasses")
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """استرجاع بيانات مهمة محددة"""
        raise NotImplementedError("This method should be implemented by subclasses")
    
    def get_agent_tasks(self, agent_id: str) -> List[Dict[str, Any]]:
        """استرجاع جميع مهام وكيل محدد"""
        raise NotImplementedError("This method should be implemented by subclasses")
    
    def update_task(self, task: Task) -> None:
        """تحديث بيانات مهمة"""
        raise NotImplementedError("This method should be implemented by subclasses")
    
    def delete_task(self, task_id: str) -> bool:
        """حذف مهمة من قاعدة البيانات"""
        raise NotImplementedError("This method should be implemented by subclasses")
    
    def log_agent_action(self, agent_id: str, action_data: Dict[str, Any]) -> None:
        """تسجيل إجراء وكيل في السجل"""
        raise NotImplementedError("This method should be implemented by subclasses")
    
    def get_agent_logs(self, agent_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """استرجاع سجل إجراءات وكيل محدد"""
        raise NotImplementedError("This method should be implemented by subclasses")