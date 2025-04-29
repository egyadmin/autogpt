"""
نقطة الدخول الرئيسية لنظام AutoGPT
"""
import os
import sys
import argparse
import logging
import importlib.util
from typing import Optional, List, Dict, Any

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("autogpt.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("autogpt")

def check_module_exists(module_name: str) -> bool:
    """التحقق من وجود وحدة بايثون"""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False

class MockTool:
    """أداة محاكاة بسيطة تستخدم عندما تكون الأدوات الأصلية غير متوفرة"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.version = "1.0"
        from datetime import datetime
        self.created_at = datetime.now()
    
    def run(self, query: str, params: Optional[str] = None) -> str:
        """تنفيذ الأداة بالمدخلات المحددة"""
        return f"[محاكاة] نتيجة من أداة {self.name}: {query[:50]}..."
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل الأداة إلى قاموس للتخزين"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "created_at": self.created_at.isoformat()
        }

def create_mock_tool(name: str, description: str) -> Any:
    """إنشاء أداة محاكاة بسيطة"""
    return MockTool(name, description)

def add_project_root_to_path():
    """إضافة مجلد المشروع الجذر إلى مسار بايثون لتسهيل الاستيرادات"""
    # الحصول على المسار المطلق للملف الحالي
    current_file_path = os.path.abspath(__file__)
    # الحصول على المجلد الحالي
    current_dir = os.path.dirname(current_file_path)
    # إضافة المسار إلى sys.path إذا لم يكن موجوداً بالفعل
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

def main():
    """الوظيفة الرئيسية للبرنامج"""
    # إضافة مجلد المشروع إلى مسار بايثون
    add_project_root_to_path()
    
    parser = argparse.ArgumentParser(description='AutoGPT - نظام وكلاء الذكاء الاصطناعي')
    parser.add_argument('--llm', default='mock', help='مزود النموذج اللغوي (openai, claude, llama, mock)')
    parser.add_argument('--db', default='memory', help='مزود قاعدة البيانات (memory, sqlite, mongodb)')
    parser.add_argument('--learning', action='store_true', help='تفعيل خدمة التعلم')
    parser.add_argument('--web', action='store_true', help='تشغيل واجهة الويب')
    parser.add_argument('--host', default='127.0.0.1', help='مضيف خادم الويب')
    parser.add_argument('--port', type=int, default=5000, help='منفذ خادم الويب')
    
    args = parser.parse_args()
    
    # التحقق من وجود الوحدات الرئيسية
    required_modules = ["core.autogpt", "core.agent", "core.task"]
    missing_modules = []
    
    for module in required_modules:
        if not check_module_exists(module):
            missing_modules.append(module)
    
    if missing_modules:
        logger.error(f"الوحدات التالية مفقودة: {', '.join(missing_modules)}")
        print(f"⛔ خطأ: الوحدات التالية مفقودة: {', '.join(missing_modules)}")
        print("تأكد من هيكل المشروع وأن جميع الملفات في المكان الصحيح.")
        sys.exit(1)
    
    # استيراد الوحدات المطلوبة
    from core.autogpt import AutoGPT
    
    # إنشاء نظام AutoGPT
    try:
        print(f"🚀 بدء تشغيل نظام AutoGPT مع LLM: {args.llm}, DB: {args.db}")
        system = AutoGPT(
            llm_provider=args.llm,
            db_provider=args.db,
            enable_learning=args.learning
        )
        
        # إضافة أدوات محاكاة للأدوات المفقودة
        missing_tools = []
        
        # التحقق من وجود الأدوات الرئيسية
        tool_modules = {
            "WebSearchTool": "tools.web_search",
            "ContentGeneratorTool": "tools.content_generator",
            "WebScrapingTool": "tools.web_scraping",
            "FileOperationsTool": "tools.file_operations",
            "DataAnalysisTool": "tools.data_analysis"
        }
        
        for tool_name, module_path in tool_modules.items():
            if not check_module_exists(module_path):
                missing_tools.append(tool_name)
                logger.warning(f"وحدة {module_path} مفقودة، سيتم استخدام أداة محاكاة")
                mock_tool = create_mock_tool(
                    name=tool_name,
                    description=f"أداة محاكاة لـ {tool_name}"
                )
                system.register_tool(mock_tool)
        
        if missing_tools:
            print(f"⚠️ الأدوات التالية غير متوفرة وتم استبدالها بأدوات محاكاة: {', '.join(missing_tools)}")
        
        # تشغيل واجهة الويب إذا طُلب ذلك
        if args.web:
            try:
                from web.server import WebServer
                web_server = WebServer(system, host=args.host, port=args.port)
                web_server.start()
                print(f"🌐 واجهة الويب متاحة على http://{args.host}:{args.port}")
            except ImportError:
                logger.error("وحدة web.server غير موجودة، لا يمكن تشغيل واجهة الويب")
                print("⚠️ وحدة web.server غير موجودة، تم تخطي تشغيل واجهة الويب")
        
        # إنشاء وكيل للاختبار
        available_tools = [tool["name"] for tool in system.get_available_tools()]
        print(f"📋 الأدوات المتاحة: {', '.join(available_tools)}")
        
        # استخدام الأدوات المتاحة فقط
        tools_to_use = []
        if "WebSearchTool" in available_tools:
            tools_to_use.append("WebSearchTool")
        if "ContentGeneratorTool" in available_tools:
            tools_to_use.append("ContentGeneratorTool")
            
        print(f"🔧 سيتم استخدام الأدوات التالية: {', '.join(tools_to_use)}")
        
        # إنشاء الوكيل
        agent = system.create_agent(
            name="AssistantAgent",
            goal="مساعدة المستخدم في المهام المختلفة",
            description="وكيل مساعد متعدد المهام يمكنه البحث وإنشاء المحتوى",
            tools=tools_to_use
        )
        
        print(f"🤖 تم إنشاء وكيل جديد: {agent.name} (ID: {agent.id})")
        
        # تشغيل الوكيل
        print("🚀 بدء تشغيل الوكيل...")
        agent.start()
        
        # عرض نتائج الوكيل
        print("\n📊 نتائج الوكيل:")
        for task in agent.tasks:
            task_status = task.status if hasattr(task, 'status') else "unknown"
            print(f"المهمة: {task.name} - الحالة: {task_status}")
            if hasattr(task, 'result') and task.result:
                # عرض نتيجة مختصرة
                result_preview = task.result[:100] + "..." if len(task.result) > 100 else task.result
                print(f"النتيجة: {result_preview}")
            print("---")
        
    except Exception as e:
        logger.error(f"خطأ أثناء تشغيل النظام: {str(e)}", exc_info=True)
        print(f"⛔ حدث خطأ: {str(e)}")
        # عرض تتبع الاستثناء الكامل للتصحيح
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    print("\n✅ اكتمل تنفيذ البرنامج بنجاح")

if __name__ == "__main__":
    main()