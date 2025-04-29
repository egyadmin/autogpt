"""
الفئة الرئيسية AutoGPT التي تدير النظام بأكمله
"""
import os
import logging
import sys
from typing import List, Dict, Any, Optional, Union, Tuple, Set, Callable
from datetime import datetime

# تعديل الاستيرادات من استيرادات نسبية إلى مطلقة
from core.agent import Agent
from core.task import Task, TaskStatus
from core.memory import AgentMemory

logger = logging.getLogger("autogpt")

class AutoGPT:
    """واجهة رئيسية للتفاعل مع نظام وكلاء الذكاء الاصطناعي"""
    
    def __init__(
        self, 
        llm_provider: str = "openai",
        api_key: Optional[str] = None,
        db_provider: str = "memory",
        db_connection_string: Optional[str] = None,
        enable_learning: bool = False
    ):
        # إعداد خدمة النموذج اللغوي
        self.llm_provider = llm_provider
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.llm_service = self._create_llm_service(llm_provider, self.api_key)
        
        # إعداد خدمة قاعدة البيانات
        self.db_provider = db_provider
        self.db_service = self._create_db_service(db_provider, db_connection_string)
        
        # إعداد خدمة التعلم
        self.enable_learning = enable_learning
        self.learning_service = self._create_learning_service() if enable_learning else None
        
        # تسجيل الأدوات المتاحة
        self.tool_registry = {}
        self._register_default_tools()
        
        # قائمة الوكلاء
        self.agents = {}
        
        # استعادة الوكلاء المخزنة إذا كانت قاعدة البيانات متوفرة
        if self.db_service:
            self._load_agents_from_db()
            
        logger.info(f"🚀 AutoGPT initialized with LLM: {llm_provider}, DB: {db_provider}")
    
    def _create_llm_service(self, provider: str, api_key: Optional[str] = None) -> 'LLMService':
        """إنشاء خدمة النموذج اللغوي المناسبة"""
        try:
            if provider == "openai":
                try:
                    from llm.openai_service import OpenAIService
                    return OpenAIService(api_key)
                except ImportError as e:
                    print(f"خطأ في استيراد OpenAIService: {e}")
                    print("الرجوع إلى خدمة المحاكاة...")
            elif provider == "claude":
                try:
                    from llm.anthropic_service import AnthropicService
                    return AnthropicService(api_key)
                except ImportError as e:
                    print(f"خطأ في استيراد AnthropicService: {e}")
                    print("الرجوع إلى خدمة المحاكاة...")
            elif provider == "llama":
                try:
                    from llm.llama_service import LlamaService
                    return LlamaService()
                except ImportError as e:
                    print(f"خطأ في استيراد LlamaService: {e}")
                    print("الرجوع إلى خدمة المحاكاة...")
            elif provider == "mock":
                from llm.mock_service import MockLLMService
                return MockLLMService()
            else:
                print(f"تحذير: مزود LLM غير معروف '{provider}'، استخدام خدمة المحاكاة")
                
            # إذا وصلنا إلى هنا، فهناك مشكلة، لذا نستخدم المحاكاة
            from llm.mock_service import MockLLMService
            return MockLLMService()
        
        except Exception as e:
            print(f"خطأ غير متوقع أثناء إنشاء خدمة LLM: {e}")
            print("الرجوع إلى خدمة المحاكاة...")
            
            try:
                from llm.mock_service import MockLLMService
                return MockLLMService()
            except ImportError:
                # إذا كان ملف المحاكاة غير موجود، نقوم بإنشاء فئة محاكاة مضمنة
                print("خدمة المحاكاة غير موجودة، إنشاء محاكاة مضمنة...")
                
                from llm.llm_service import LLMService
                from typing import List
                
                class InlineMockLLMService(LLMService):
                    def query(self, prompt: str, **kwargs) -> str:
                        return f"استجابة محاكاة مضمنة لاستعلام: {prompt[:50]}..."
                    
                    def get_embedding(self, text: str) -> List[float]:
                        return [0.1, 0.2, 0.3, 0.4, 0.5]  # قيم للاختبار
                
                return InlineMockLLMService()
    
    def _create_db_service(self, provider: str, connection_string: Optional[str] = None) -> Optional['DatabaseService']:
        """إنشاء خدمة قاعدة البيانات المناسبة"""
        try:
            if provider == "memory":
                from database.memory_db import MemoryDatabaseService
                return MemoryDatabaseService()
            elif provider == "sqlite":
                from database.sqlite_db import SQLiteDatabaseService
                return SQLiteDatabaseService(connection_string or "autogpt.db")
            elif provider == "mongodb":
                from database.mongo_db import MongoDatabaseService
                return MongoDatabaseService(connection_string)
            elif provider == "none":
                return None
            else:
                print(f"تحذير: مزود DB غير معروف: {provider}، استخدام قاعدة بيانات في الذاكرة")
                from database.memory_db import MemoryDatabaseService
                return MemoryDatabaseService()
        except ImportError as e:
            print(f"خطأ في استيراد خدمة قاعدة البيانات: {e}")
            print("الرجوع إلى قاعدة بيانات في الذاكرة...")
            try:
                from database.memory_db import MemoryDatabaseService
                return MemoryDatabaseService()
            except ImportError:
                print("تعذر استيراد حتى قاعدة البيانات في الذاكرة، العمل بدون تخزين")
                return None
    
    def _create_learning_service(self) -> Optional['LearningService']:
        """إنشاء خدمة التعلم"""
        try:
            from learning.learning_service import LearningService
            return LearningService()
        except ImportError as e:
            print(f"خطأ في استيراد خدمة التعلم: {e}")
            print("تعطيل خاصية التعلم...")
            return None
    
    def _register_default_tools(self) -> None:
        """تسجيل الأدوات الافتراضية"""
        try:
            # محاولة استيراد الأدوات الأساسية
            tool_modules = [
                ("tools.web_search", "WebSearchTool"),
                ("tools.web_scraping", "WebScrapingTool"),
                ("tools.file_operations", "FileOperationsTool"),
                ("tools.data_analysis", "DataAnalysisTool"),
                ("tools.content_generator", "ContentGeneratorTool")
            ]
            
            for module_path, class_name in tool_modules:
                try:
                    module = __import__(module_path, fromlist=[class_name])
                    tool_class = getattr(module, class_name)
                    tool = tool_class()
                    self.register_tool(tool)
                except (ImportError, AttributeError) as e:
                    print(f"تعذر تحميل الأداة {class_name}: {e}")
                    
        except Exception as e:
            print(f"خطأ أثناء تسجيل الأدوات الافتراضية: {e}")
            print("تخطي تسجيل الأدوات...")
    
    def register_tool(self, tool: 'Tool') -> None:
        """تسجيل أداة جديدة في النظام"""
        self.tool_registry[tool.name] = tool
        logger.info(f"Tool registered: {tool.name}")
    
    def _load_agents_from_db(self) -> None:
        """تحميل الوكلاء المخزنة من قاعدة البيانات"""
        if not self.db_service:
            return
            
        try:
            agent_dicts = self.db_service.get_all_agents()
            for agent_dict in agent_dicts:
                agent = Agent.from_dict(
                    agent_dict, 
                    self.llm_service, 
                    self.db_service,
                    self.tool_registry,
                    self.learning_service
                )
                self.agents[agent.id] = agent
                logger.info(f"Loaded agent from database: {agent.name} (ID: {agent.id})")
        except Exception as e:
            print(f"خطأ أثناء تحميل الوكلاء من قاعدة البيانات: {e}")
    
    def create_agent(
        self, 
        name: str, 
        goal: str, 
        description: Optional[str] = None,
        creator_id: Optional[str] = None,
        tools: Optional[List[str]] = None
    ) -> Agent:
        """إنشاء وكيل جديد بهدف محدد"""
        # تجميع الأدوات المطلوبة
        agent_tools = []
        if tools:
            for tool_name in tools:
                if tool_name in self.tool_registry:
                    agent_tools.append(self.tool_registry[tool_name])
        
        # إنشاء الوكيل
        agent = Agent(
            name=name, 
            goal=goal, 
            llm_service=self.llm_service,
            db_service=self.db_service,
            description=description,
            creator_id=creator_id,
            tools=agent_tools,
            learning_service=self.learning_service
        )
        
        # تسجيل الوكيل
        self.agents[agent.id] = agent
        
        # حفظ الوكيل في قاعدة البيانات إذا كانت متاحة
        if self.db_service:
            self.db_service.save_agent(agent)
            
        logger.info(f"Created new agent: {name} (ID: {agent.id})")
        return agent
    
    def list_agents(self, creator_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """الحصول على قائمة جميع الوكلاء المتاحين"""
        agents_list = []
        for agent_id, agent in self.agents.items():
            if creator_id and agent.creator_id != creator_id:
                continue
                
            agents_list.append({
                "id": agent.id,
                "name": agent.name,
                "goal": agent.goal,
                "description": agent.description,
                "is_running": agent.is_running,
                "is_paused": agent.is_paused if hasattr(agent, 'is_paused') else False,
                "creator_id": agent.creator_id,
                "created_at": agent.created_at.isoformat(),
                "status": agent.get_status() if hasattr(agent, 'get_status') else {}
            })
            
        return agents_list
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """الحصول على وكيل معين بالمعرف"""
        return self.agents.get(agent_id)
    
    def delete_agent(self, agent_id: str) -> bool:
        """حذف وكيل"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            
            # إيقاف الوكيل إذا كان قيد التشغيل
            if agent.is_running:
                agent.stop()
                
            # حذف الوكيل من قاعدة البيانات إذا كانت متاحة
            if self.db_service:
                self.db_service.delete_agent(agent_id)
                
            # حذف الوكيل من القائمة
            del self.agents[agent_id]
            
            logger.info(f"Deleted agent ID: {agent_id}")
            return True
            
        return False
    
    def get_available_tools(self) -> List[Dict[str, str]]:
        """الحصول على قائمة الأدوات المتاحة في النظام"""
        return [
            {"name": name, "description": tool.description}
            for name, tool in self.tool_registry.items()
        ]
    
    def get_agent_tasks(self, agent_id: str, include_subtasks: bool = True) -> List[Dict[str, Any]]:
        """الحصول على قائمة مهام الوكيل"""
        agent = self.get_agent(agent_id)
        if not agent:
            return []
            
        return [task.to_dict(include_subtasks) for task in agent.tasks]
    
    def get_agent_history(self, agent_id: str) -> List[Dict[str, Any]]:
        """الحصول على سجل إجراءات الوكيل"""
        agent = self.get_agent(agent_id)
        if not agent:
            return []
            
        return agent.history
    
    def save_state(self) -> None:
        """حفظ حالة النظام بالكامل"""
        if not self.db_service:
            logger.warning("Cannot save state: no database service available")
            return
            
        for agent in self.agents.values():
            self.db_service.save_agent(agent)
            
        logger.info(f"Saved state with {len(self.agents)} agents")
    
    def load_state(self) -> None:
        """تحميل حالة النظام"""
        self._load_agents_from_db()
        logger.info(f"Loaded state with {len(self.agents)} agents")