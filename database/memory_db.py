"""
قاعدة بيانات في الذاكرة للتطوير والاختبار
"""
from typing import List, Dict, Any, Optional
import json
import copy
from datetime import datetime

from .db_service import DatabaseService

class MemoryDatabaseService(DatabaseService):
    """خدمة قاعدة بيانات في الذاكرة للتطوير والاختبار"""
    
    def __init__(self):
        self.agents = {}  # agent_id -> agent_data
        self.tasks = {}   # task_id -> task_data
        self.logs = {}    # agent_id -> [log_entries]
    
    def save_agent(self, agent) -> None:
        """حفظ بيانات الوكيل"""
        agent_dict = agent.to_dict()
        self.agents[agent.id] = copy.deepcopy(agent_dict)
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """استرجاع بيانات وكيل محدد"""
        return copy.deepcopy(self.agents.get(agent_id))
    
    def get_all_agents(self, creator_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """استرجاع بيانات جميع الوكلاء"""
        if creator_id:
            return [
                copy.deepcopy(agent_data) for agent_data in self.agents.values()
                if agent_data.get("creator_id") == creator_id
            ]
        else:
            return [copy.deepcopy(agent_data) for agent_data in self.agents.values()]
    
    def delete_agent(self, agent_id: str) -> bool:
        """حذف وكيل من قاعدة البيانات"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            
            # حذف مهام الوكيل
            task_ids_to_delete = [
                task_id for task_id, task_data in self.tasks.items()
                if task_data.get("agent_id") == agent_id
            ]
            for task_id in task_ids_to_delete:
                del self.tasks[task_id]
                
            # حذف سجلات الوكيل
            if agent_id in self.logs:
                del self.logs[agent_id]
                
            return True
        return False
    
    def save_task(self, task) -> None:
        """حفظ بيانات المهمة"""
        task_dict = task.to_dict()
        self.tasks[task.id] = copy.deepcopy(task_dict)
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """استرجاع بيانات مهمة محددة"""
        return copy.deepcopy(self.tasks.get(task_id))
    
    def get_agent_tasks(self, agent_id: str) -> List[Dict[str, Any]]:
        """استرجاع جميع مهام وكيل محدد"""
        return [
            copy.deepcopy(task_data) for task_data in self.tasks.values()
            if task_data.get("agent_id") == agent_id
        ]
    
    def update_task(self, task) -> None:
        """تحديث بيانات مهمة"""
        self.save_task(task)
    
    def delete_task(self, task_id: str) -> bool:
        """حذف مهمة من قاعدة البيانات"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False
    
    def log_agent_action(self, agent_id: str, action_data: Dict[str, Any]) -> None:
        """تسجيل إجراء وكيل في السجل"""
        if agent_id not in self.logs:
            self.logs[agent_id] = []
            
        self.logs[agent_id].append(copy.deepcopy(action_data))
    
    def get_agent_logs(self, agent_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """استرجاع سجل إجراءات وكيل محدد"""
        if agent_id not in self.logs:
            return []
            
        logs = self.logs[agent_id]
        if limit > 0:
            logs = logs[-limit:]
            
        return copy.deepcopy(logs)