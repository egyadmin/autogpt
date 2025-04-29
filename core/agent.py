"""
وكيل ذكاء اصطناعي مستقل يمكنه تنفيذ المهام
"""
import uuid
import time
import json
import logging
import threading
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from core.task import Task, TaskStatus
from core.memory import AgentMemory

logger = logging.getLogger("autogpt")

class Agent:
    """وكيل ذكاء اصطناعي مستقل يمكنه تنفيذ المهام"""
    
    def __init__(
        self, 
        name: str, 
        goal: str, 
        llm_service: 'LLMService',
        db_service: Optional['DatabaseService'] = None,
        agent_id: Optional[str] = None,
        description: Optional[str] = None,  # إضافة معلمة description
        creator_id: Optional[str] = None,
        tools: Optional[List['Tool']] = None,
        learning_service: Optional['LearningService'] = None
    ):
        self.id = agent_id or str(uuid.uuid4())
        self.name = name
        self.goal = goal
        self.description = description or f"وكيل لتنفيذ المهام المتعلقة بـ: {goal}"  # تعيين الوصف
        self.creator_id = creator_id
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        self.llm_service = llm_service
        self.db_service = db_service
        self.tools = tools or []
        self.learning_service = learning_service
        self.tasks: List[Task] = []
        self.history: List[Dict[str, Any]] = []
        self.is_running = False
        self.memory = AgentMemory()
        self.thread_executor = ThreadPoolExecutor(max_workers=5)
        self.status_lock = threading.Lock()
        self.is_paused = False
        
    def add_task(self, name: str, description: str, priority: int = 5, tags: Optional[List[str]] = None) -> Task:
        """إضافة مهمة جديدة إلى قائمة المهام"""
        task = Task(
            name=name, 
            description=description, 
            agent_id=self.id,
            priority=priority,
            tags=tags or []
        )
        
        self.tasks.append(task)
        
        # حفظ المهمة في قاعدة البيانات إذا كانت متاحة
        if self.db_service:
            self.db_service.save_task(task)
            
        return task
    
    def start(self, async_mode: bool = False) -> Union[None, threading.Thread]:
        """بدء تشغيل الوكيل لتنفيذ المهام"""
        with self.status_lock:
            self.is_running = True
            self.is_paused = False
            
        logger.info(f"🤖 Agent '{self.name}' starting with goal: {self.goal}")
        self._log_action("Agent Started", f"Starting with goal: {self.goal}")
        
        # إذا لم تكن هناك مهام، قم بإنشاء مهمة أولية استنادًا إلى الهدف
        if not self.tasks:
            main_task = self.add_task("Main Goal", self.goal, priority=10, tags=["main", "auto-generated"])
            self._break_down_task(main_task)
        
        if async_mode:
            thread = threading.Thread(target=self._run_tasks)
            thread.daemon = True
            thread.start()
            return thread
        else:
            self._run_tasks()
            return None
    
    def _run_tasks(self) -> None:
        """تنفيذ المهام في حلقة"""
        try:
            # ترتيب المهام حسب الأولوية
            sorted_tasks = sorted(
                self.tasks, 
                key=lambda task: (-task.priority, task.created_at)
            )
            
            while self.is_running and any(task.status == TaskStatus.PENDING for task in sorted_tasks):
                # التحقق مما إذا كان الوكيل متوقفًا مؤقتًا
                if self.is_paused:
                    time.sleep(1)  # انتظار قبل التحقق مرة أخرى
                    continue
                    
                for task in sorted_tasks:
                    if task.status == TaskStatus.PENDING:
                        self._execute_task(task)
                
                # إعادة ترتيب المهام لمراعاة المهام الجديدة
                sorted_tasks = sorted(
                    self.tasks, 
                    key=lambda task: (-task.priority, task.created_at)
                )
                
            if self.is_running:  # لم يتم إيقافه من خلال stop()
                logger.info(f"🏁 Agent '{self.name}' completed all tasks!")
                self._log_action("All Tasks Completed", "Agent finished executing all tasks")
                
                # تعلم من التجربة إذا كانت خدمة التعلم متوفرة
                if self.learning_service:
                    self.learning_service.learn_from_execution(self)
                    
                with self.status_lock:
                    self.is_running = False
        except Exception as e:
            logger.error(f"Error in agent execution: {str(e)}", exc_info=True)
            self._log_action("Agent Error", f"Error during execution: {str(e)}")
            with self.status_lock:
                self.is_running = False
    
    def stop(self) -> None:
        """إيقاف تشغيل الوكيل"""
        with self.status_lock:
            if self.is_running:
                self.is_running = False
                logger.info(f"🛑 Agent '{self.name}' stopped")
                self._log_action("Agent Stopped", "Manual stop requested")
    
    def pause(self) -> None:
        """إيقاف تشغيل الوكيل مؤقتًا"""
        with self.status_lock:
            if self.is_running:
                self.is_paused = True
                logger.info(f"⏸️ Agent '{self.name}' paused")
                self._log_action("Agent Paused", "Execution paused")
    
    def resume(self) -> None:
        """استئناف تشغيل الوكيل بعد الإيقاف المؤقت"""
        with self.status_lock:
            if self.is_running and self.is_paused:
                self.is_paused = False
                logger.info(f"▶️ Agent '{self.name}' resumed")
                self._log_action("Agent Resumed", "Execution resumed")
    
    def get_status(self) -> Dict[str, Any]:
        """الحصول على حالة الوكيل الحالية"""
        total_tasks = len(self.tasks)
        pending_tasks = sum(1 for task in self.tasks if task.status == TaskStatus.PENDING)
        in_progress_tasks = sum(1 for task in self.tasks if task.status == TaskStatus.IN_PROGRESS)
        completed_tasks = sum(1 for task in self.tasks if task.status == TaskStatus.COMPLETED)
        failed_tasks = sum(1 for task in self.tasks if task.status == TaskStatus.FAILED)
        
        return {
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "total_tasks": total_tasks,
            "pending_tasks": pending_tasks,
            "in_progress_tasks": in_progress_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "completion_percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        }
    
    def add_tool(self, tool: 'Tool') -> None:
        """إضافة أداة جديدة للوكيل"""
        self.tools.append(tool)
        logger.info(f"Tool '{tool.name}' added to agent '{self.name}'")
    
    def get_available_tools(self) -> List[Dict[str, str]]:
        """الحصول على قائمة الأدوات المتاحة للوكيل"""
        return [{"name": tool.name, "description": tool.description} for tool in self.tools]
    
    def find_tool(self, tool_name: str) -> Optional['Tool']:
        """البحث عن أداة بالاسم"""
        for tool in self.tools:
            if tool.name.lower() == tool_name.lower():
                return tool
        return None
    
    def _log_action(self, action: str, details: Any) -> None:
        """تسجيل إجراء في سجل الوكيل"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        self.history.append(entry)
        
        # حفظ الإجراء في قاعدة البيانات إذا كانت متاحة
        if self.db_service:
            self.db_service.log_agent_action(self.id, entry)
            
        logger.info(f"Agent '{self.name}': {action} - {details}")
    
    def _break_down_task(self, task: Task) -> None:
        """تقسيم مهمة إلى مهام فرعية باستخدام نموذج لغوي"""
        self._log_action("Task Breakdown Started", f"Breaking down task: {task.name}")
        task.update_status(TaskStatus.IN_PROGRESS)
        
        # إنشاء سياق لتحليل المهمة
        context = {
            "agent_goal": self.goal,
            "task_name": task.name,
            "task_description": task.description,
            "available_tools": self.get_available_tools()
        }
        
        prompt = f"""
        أنت وكيل ذكاء اصطناعي مهمتك تقسيم المهام إلى خطوات أصغر وأكثر قابلية للتنفيذ.
        
        هدفك العام: {self.goal}
        
        المهمة التي تحتاج إلى تقسيمها:
        اسم: {task.name}
        وصف: {task.description}
        
        الأدوات المتاحة لك:
        {json.dumps(self.get_available_tools(), ensure_ascii=False, indent=2)}
        
        قم بتقسيم هذه المهمة إلى خطوات أصغر (3-7 خطوات) تكون منطقية ومترابطة.
        
        قدم الإجابة بتنسيق JSON كما يلي:
        {{
            "subtasks": [
                {{
                    "name": "اسم المهمة الفرعية 1",
                    "description": "وصف تفصيلي للمهمة 1",
                    "priority": 5,
                    "tools": ["اسم_الأداة_1", "اسم_الأداة_2"]
                }},
                ...
            ]
        }}
        """
        
        try:
            response = self.llm_service.query(prompt, context=context)
            self._log_action("LLM Response", f"Received response for task breakdown")
            
            try:
                # محاولة تحليل الاستجابة كـ JSON
                result = json.loads(response)
                if "subtasks" in result:
                    for subtask_info in result["subtasks"]:
                        priority = subtask_info.get("priority", 5)
                        subtask = task.add_subtask(
                            subtask_info["name"], 
                            subtask_info["description"],
                            priority=priority
                        )
                        
                        # حفظ المهمة الفرعية في قاعدة البيانات إذا كانت متاحة
                        if self.db_service:
                            self.db_service.save_task(subtask)
                            
                        # إضافة بيانات وصفية حول الأدوات المقترحة
                        if "tools" in subtask_info:
                            subtask.add_metadata("suggested_tools", subtask_info["tools"])
                    
                    self._log_action(
                        "Task Breakdown Completed", 
                        f"Divided '{task.name}' into {len(task.subtasks)} subtasks"
                    )
                    return
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse LLM response as JSON: {str(e)}")
                logger.debug(f"Raw response: {response}")
                
            # إذا وصلنا إلى هنا، فقد فشل التحليل، لذا نحاول مرة أخرى بتوجيهات أكثر صرامة
            fallback_prompt = f"""
            لم أتمكن من فهم استجابتك السابقة. من فضلك قم بتقسيم المهمة "{task.description}" إلى خطوات أصغر.
            
            قدم الإجابة فقط بتنسيق JSON التالي:
            {{
                "subtasks": [
                    {{
                        "name": "اسم المهمة الفرعية",
                        "description": "وصف تفصيلي"
                    }},
                    ...
                ]
            }}
            """
            
            response = self.llm_service.query(fallback_prompt)
            try:
                result = json.loads(response)
                if "subtasks" in result:
                    for subtask_info in result["subtasks"]:
                        subtask = task.add_subtask(
                            subtask_info["name"], 
                            subtask_info["description"]
                        )
                        if self.db_service:
                            self.db_service.save_task(subtask)
                    
                    self._log_action(
                        "Task Breakdown Completed (Fallback)", 
                        f"Divided '{task.name}' into {len(task.subtasks)} subtasks using fallback method"
                    )
                    return
            except (json.JSONDecodeError, KeyError):
                pass
                
            # إذا استمر الفشل، نقوم بإنشاء مهام فرعية افتراضية
            self._log_action(
                "Task Breakdown Failed", 
                f"Could not break down '{task.name}' properly. Creating default subtasks."
            )
            
            default_subtasks = [
                {"name": "Research", "description": f"Gather information about {task.description}"},
                {"name": "Analysis", "description": f"Analyze the information related to {task.description}"},
                {"name": "Execution", "description": f"Execute the primary actions for {task.description}"},
                {"name": "Summary", "description": f"Summarize findings and results from {task.description}"}
            ]
            
            for subtask_info in default_subtasks:
                subtask = task.add_subtask(subtask_info["name"], subtask_info["description"])
                if self.db_service:
                    self.db_service.save_task(subtask)
                    
        except Exception as e:
            logger.error(f"Error in task breakdown: {str(e)}", exc_info=True)
            self._log_action("Task Breakdown Error", f"Error: {str(e)}")
            task.fail(f"Could not break down task: {str(e)}")
    
    def _execute_task(self, task: Task) -> None:
        """تنفيذ مهمة محددة"""
        self._log_action("Task Started", f"Executing '{task.name}'")
        task.update_status(TaskStatus.IN_PROGRESS)
        
        # حفظ المهمة المحدثة في قاعدة البيانات إذا كانت متاحة
        if self.db_service:
            self.db_service.update_task(task)
            
        # إذا كانت المهمة لديها مهام فرعية، قم بتنفيذها أولاً
        if task.subtasks:
            # ترتيب المهام الفرعية حسب الأولوية
            sorted_subtasks = sorted(
                task.subtasks, 
                key=lambda subtask: (-subtask.priority, subtask.created_at)
            )
            
            for subtask in sorted_subtasks:
                if subtask.status == TaskStatus.PENDING:
                    self._execute_task(subtask)
            
            # تحقق مما إذا كانت جميع المهام الفرعية مكتملة
            if all(subtask.status == TaskStatus.COMPLETED for subtask in task.subtasks):
                # جمع نتائج المهام الفرعية
                results = [f"{subtask.name}: {subtask.result}" for subtask in task.subtasks]
                results_text = "\n".join(results)
                
                summary_prompt = f"""
                أنت وكيل ذكاء اصطناعي تقوم بتلخيص وتجميع نتائج المهام الفرعية في نتيجة واحدة شاملة.
                
                المهمة الرئيسية: {task.name}
                وصف المهمة: {task.description}
                
                نتائج المهام الفرعية:
                {results_text}
                
                قم بتلخيص هذه النتائج في إجابة شاملة ومتماسكة. قدم تحليلاً للنتائج واستنتاجات نهائية.
                """
                
                try:
                    final_result = self.llm_service.query(summary_prompt)
                    task.complete(final_result)
                    self._log_action("Task Completed", f"'{task.name}' completed with all subtasks")
                    
                    # حفظ المهمة المكتملة في قاعدة البيانات إذا كانت متاحة
                    if self.db_service:
                        self.db_service.update_task(task)
                        
                    # حفظ التجربة في الذاكرة للتعلم
                    self.memory.add_memory(
                        "completed_task",
                        {
                            "task_name": task.name,
                            "task_description": task.description,
                            "result": final_result,
                            "subtasks": [subtask.to_dict(include_subtasks=False) for subtask in task.subtasks]
                        },
                        metadata={"success": True}
                    )
                except Exception as e:
                    logger.error(f"Error generating summary: {str(e)}", exc_info=True)
                    task.fail(f"Error generating summary: {str(e)}")
            else:
                # إذا فشلت أي من المهام الفرعية
                failed_subtasks = [subtask for subtask in task.subtasks if subtask.status == TaskStatus.FAILED]
                reasons = [f"{subtask.name}: {subtask.error_message}" for subtask in failed_subtasks]
                failure_details = "\n".join(reasons)
                task.fail(f"Subtasks failed: {failure_details}")
                self._log_action("Task Failed", f"'{task.name}' failed due to subtask failures")
                
                # حفظ المهمة الفاشلة في قاعدة البيانات إذا كانت متاحة
                if self.db_service:
                    self.db_service.update_task(task)
                    
                # حفظ التجربة في الذاكرة للتعلم
                self.memory.add_memory(
                    "failed_task",
                    {
                        "task_name": task.name,
                        "task_description": task.description,
                        "error": failure_details,
                        "subtasks": [subtask.to_dict(include_subtasks=False) for subtask in task.subtasks]
                    },
                    metadata={"success": False}
                )
        else:
            # إذا لم تكن هناك مهام فرعية، قم بتنفيذ المهمة مباشرة
            try:
                # تحقق مما إذا كانت المهمة تتطلب أدوات محددة
                required_tools = []
                if hasattr(task, 'metadata') and "suggested_tools" in task.metadata:
                    required_tools = [
                        self.find_tool(tool_name) 
                        for tool_name in task.metadata["suggested_tools"]
                        if self.find_tool(tool_name) is not None
                    ]
                
                # إنشاء سياق للمهمة
                context = {
                    "agent_goal": self.goal,
                    "task_name": task.name,
                    "task_description": task.description,
                    "available_tools": self.get_available_tools()
                }
                
                # إنشاء نص توجيهي للنموذج اللغوي
                prompt = f"""
                أنت وكيل ذكاء اصطناعي مهمتك تنفيذ المهمة التالية بناءً على المعلومات المقدمة.
                
                الهدف العام: {self.goal}
                
                المهمة المطلوب تنفيذها:
                اسم: {task.name}
                وصف: {task.description}
                
                الأدوات المتاحة لك:
                {json.dumps(self.get_available_tools(), ensure_ascii=False, indent=2)}
                
                قم بتنفيذ المهمة وتقديم نتيجة مفصلة وشاملة.
                """
                
                # تنفيذ المهمة باستخدام النموذج اللغوي
                result = self.llm_service.query(prompt, context=context)
                
                # استخدام الأدوات إذا كانت مطلوبة
                if required_tools:
                    tool_results = []
                    for tool in required_tools:
                        tool_prompt = f"""
                        أنا بحاجة إلى استخدام أداة "{tool.name}" لتنفيذ مهمة:
                        {task.description}
                        
                        وصف الأداة: {tool.description}
                        
                        كيف يمكنني استخدام هذه الأداة بشكل فعال لتنفيذ المهمة؟ قدم مدخلات دقيقة وتفصيلية لاستخدام الأداة.
                        """
                        
                        tool_instructions = self.llm_service.query(tool_prompt)
                        
                        try:
                            # استدعاء الأداة بالمدخلات المقترحة
                            tool_result = tool.run(task.description, tool_instructions)
                            tool_results.append(f"نتيجة أداة {tool.name}: {tool_result}")
                        except Exception as e:
                            tool_results.append(f"فشل تنفيذ أداة {tool.name}: {str(e)}")
                    
                    # دمج نتائج الأدوات مع النتيجة الرئيسية
                    if tool_results:
                        tools_output = "\n".join(tool_results)
                        integration_prompt = f"""
                        لقد قمت بتنفيذ المهمة:
                        {task.description}
                        
                        وتوصلت إلى النتيجة التالية:
                        {result}
                        
                        كما استخدمت الأدوات التالية:
                        {tools_output}
                        
                        قم بدمج نتائج الأدوات مع النتيجة الرئيسية لتقديم إجابة شاملة ومتكاملة.
                        """
                        
                        result = self.llm_service.query(integration_prompt)
                
                # إكمال المهمة بنجاح
                task.complete(result)
                self._log_action("Task Completed", f"'{task.name}' executed directly")
                
                # حفظ المهمة المكتملة في قاعدة البيانات إذا كانت متاحة
                if self.db_service:
                    self.db_service.update_task(task)
                    
                # حفظ التجربة في الذاكرة للتعلم
                self.memory.add_memory(
                    "direct_task",
                    {
                        "task_name": task.name,
                        "task_description": task.description,
                        "prompt": prompt,
                        "result": result,
                        "tools_used": [tool.name for tool in required_tools] if required_tools else []
                    },
                    metadata={"success": True}
                )
            except Exception as e:
                logger.error(f"Error in direct task execution: {str(e)}", exc_info=True)
                task.fail(str(e))
                self._log_action("Task Failed", f"'{task.name}' failed with error: {str(e)}")
                
                # حفظ المهمة الفاشلة في قاعدة البيانات إذا كانت متاحة
                if self.db_service:
                    self.db_service.update_task(task)
                    
                # حفظ التجربة في الذاكرة للتعلم
                self.memory.add_memory(
                    "direct_task",
                    {
                        "task_name": task.name,
                        "task_description": task.description,
                        "error": str(e)
                    },
                    metadata={"success": False}
                )
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل الوكيل إلى قاموس للتخزين"""
        return {
            "id": self.id,
            "name": self.name,
            "goal": self.goal,
            "description": self.description,
            "creator_id": self.creator_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "tasks": [task.to_dict() for task in self.tasks],
            "history": self.history,
            "memory": self.memory.to_dict(),
            "tools": [tool.to_dict() for tool in self.tools]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], llm_service: 'LLMService', 
                 db_service: Optional['DatabaseService'] = None,
                 tool_registry: Optional[Dict[str, 'Tool']] = None,
                 learning_service: Optional['LearningService'] = None) -> 'Agent':
        """استعادة وكيل من قاموس"""
        agent = cls(
            name=data["name"],
            goal=data["goal"],
            llm_service=llm_service,
            db_service=db_service,
            agent_id=data["id"],
            description=data.get("description"),
            creator_id=data.get("creator_id"),
            learning_service=learning_service
        )
        
        # تحويل التواريخ من النص إلى كائنات datetime
        if "created_at" in data:
            agent.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            agent.updated_at = datetime.fromisoformat(data["updated_at"])
            
        agent.is_running = data.get("is_running", False)
        agent.is_paused = data.get("is_paused", False)
        agent.history = data.get("history", [])
        
        # استعادة المهام
        if "tasks" in data:
            for task_data in data["tasks"]:
                task = Task.from_dict(task_data)
                agent.tasks.append(task)
                
        # استعادة الذاكرة
        if "memory" in data:
            agent.memory = AgentMemory.from_dict(data["memory"])
            
        # استعادة الأدوات
        if "tools" in data and tool_registry:
            for tool_data in data["tools"]:
                if tool_data["name"] in tool_registry:
                    agent.tools.append(tool_registry[tool_data["name"]])
                    
        return agent