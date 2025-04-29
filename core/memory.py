"""
وحدة ذاكرة الوكيل
================
توفر هذه الوحدة نظام تخزين وإدارة ذاكرة الوكيل الذكي.
"""

import uuid
import hashlib
import random
from typing import List, Dict, Any, Optional
from datetime import datetime

class AgentMemory:
    """تخزين مؤقت لذاكرة الوكيل وتجاربه السابقة"""
    
    def __init__(self, max_items: int = 1000):
        self.memory_items: List[Dict[str, Any]] = []
        self.max_items = max_items
        self.knowledge_base: Dict[str, Any] = {}
        self.last_accessed = {}
    
    def add_memory(self, memory_type: str, content: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """إضافة عنصر إلى الذاكرة"""
        memory_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        memory_item = {
            "id": memory_id,
            "type": memory_type,
            "content": content,
            "created_at": timestamp,
            "last_accessed": timestamp,
            "access_count": 0,
            "metadata": metadata or {}
        }
        
        self.memory_items.append(memory_item)
        
        # إذا تجاوزنا الحد الأقصى، قم بإزالة العناصر الأقدم
        if len(self.memory_items) > self.max_items:
            # ترتيب العناصر حسب تاريخ آخر وصول وعدد مرات الوصول
            sorted_items = sorted(
                self.memory_items,
                key=lambda x: (x["last_accessed"], x["access_count"])
            )
            # حذف أقدم 10% من العناصر
            items_to_remove = int(self.max_items * 0.1)
            self.memory_items = sorted_items[items_to_remove:]
            
        return memory_id
    
    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """استرجاع عنصر من الذاكرة حسب المعرف"""
        for item in self.memory_items:
            if item["id"] == memory_id:
                # تحديث معلومات الوصول
                item["last_accessed"] = datetime.now()
                item["access_count"] += 1
                return item
                
        return None
    
    def search_memory(self, query: str, memory_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """البحث في الذاكرة حسب الاستعلام ونوع الذاكرة"""
        # في تطبيق حقيقي، يمكن استخدام محرك بحث أكثر تطوراً
        # مثل Elastic Search أو تقنيات البحث الدلالي
        
        matching_items = []
        query = query.lower()
        
        for item in self.memory_items:
            if memory_type and item["type"] != memory_type:
                continue
                
            content_str = str(item["content"]).lower()
            
            if query in content_str:
                # تحديث تاريخ آخر وصول وعدد مرات الوصول
                item["last_accessed"] = datetime.now()
                item["access_count"] += 1
                matching_items.append(item)
                
                if len(matching_items) >= limit:
                    break
                    
        return matching_items
    
    def add_to_knowledge_base(self, key: str, value: Any) -> None:
        """إضافة معلومات إلى قاعدة المعرفة"""
        self.knowledge_base[key] = {
            "value": value,
            "created_at": datetime.now(),
            "last_accessed": datetime.now(),
            "access_count": 0
        }
    
    def get_from_knowledge_base(self, key: str) -> Any:
        """استرجاع معلومات من قاعدة المعرفة"""
        if key in self.knowledge_base:
            # تحديث معلومات الوصول
            self.knowledge_base[key]["last_accessed"] = datetime.now()
            self.knowledge_base[key]["access_count"] += 1
            return self.knowledge_base[key]["value"]
            
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل الذاكرة إلى قاموس للتخزين"""
        return {
            "memory_items": self.memory_items,
            "knowledge_base": self.knowledge_base
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMemory':
        """استعادة الذاكرة من قاموس"""
        memory = cls()
        memory.memory_items = data.get("memory_items", [])
        memory.knowledge_base = data.get("knowledge_base", {})
        return memory
        
    def search_semantic(self, query_embedding: List[float], memory_type: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """البحث الدلالي باستخدام التمثيلات الشعاعية (مبسط)"""
        # في تطبيق حقيقي، استخدم FAISS أو مكتبة مشابهة
        
        # وظيفة مبسطة لحساب التشابه (جيب التمام)
        def cosine_similarity(vec1, vec2):
            if not hasattr(vec2, "__iter__"):
                return 0
            dot_product = sum(a * b for a, b in zip(vec1, vec2[:len(vec1)]))
            magnitude1 = sum(a * a for a in vec1) ** 0.5
            magnitude2 = sum(b * b for b in vec2[:len(vec1)]) ** 0.5
            if magnitude1 * magnitude2 == 0:
                return 0
            return dot_product / (magnitude1 * magnitude2)
            
        # محاكاة بسيطة للبحث الدلالي
        results = []
        for item in self.memory_items:
            if memory_type and item["type"] != memory_type:
                continue
                
            # إنشاء تمثيل شعاعي وهمي للعنصر (في تطبيق حقيقي، هذا سيكون مخزناً)
            content_str = str(item["content"])
            content_hash = hashlib.md5(content_str.encode()).hexdigest()
            random.seed(int(content_hash, 16))
            content_embedding = [random.uniform(-1, 1) for _ in range(len(query_embedding))]
            
            # حساب التشابه
            similarity = cosine_similarity(query_embedding, content_embedding)
            
            if similarity > 0.7:  # عتبة التشابه
                results.append({
                    "item": item,
                    "similarity": similarity
                })
                
        # ترتيب النتائج حسب التشابه
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        # تحديث معلومات الوصول للعناصر المسترجعة
        for result in results[:limit]:
            item = result["item"]
            item["last_accessed"] = datetime.now()
            item["access_count"] += 1
            
        return [result["item"] for result in results[:limit]]