"""
خدمة محاكاة للنماذج اللغوية للاختبار والعرض التوضيحي
"""
import hashlib
import json
import random
from typing import List, Dict, Any, Optional
from .llm_service import LLMService

class MockLLMService(LLMService):
    """خدمة محاكاة للنموذج اللغوي للاختبار والعرض التوضيحي"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.response_templates = {
            "breakdown": {
                "subtasks": [
                    {"name": "مرحلة البحث", "description": "جمع المعلومات حول الموضوع", "priority": 7, "tools": ["WebSearchTool", "WebScrapingTool"]},
                    {"name": "مرحلة التحليل", "description": "تحليل المعلومات التي تم جمعها", "priority": 5, "tools": ["DataAnalysisTool"]},
                    {"name": "إنشاء المحتوى", "description": "إنشاء محتوى بناءً على التحليل", "priority": 6, "tools": ["ContentGeneratorTool"]},
                    {"name": "مرحلة التلخيص", "description": "تلخيص النتائج واستخلاص الاستنتاجات", "priority": 4}
                ]
            }
        }
    
    def query(self, prompt: str, context: Optional[Dict[str, Any]] = None, **kwargs) -> str:
        """إرسال استعلام إلى النموذج اللغوي المحاكي واسترجاع الاستجابة"""
        print(f"[MockLLM] تم استلام استعلام: {prompt[:100]}...")
        
        # تحليل نوع الاستعلام
        prompt_lower = prompt.lower()
        
        if "break down" in prompt_lower or "تقسيم" in prompt_lower or "خطوات" in prompt_lower:
            return json.dumps(self.response_templates["breakdown"], ensure_ascii=False)
        elif "research" in prompt_lower or "بحث" in prompt_lower:
            if context and "task_description" in context:
                return f"نتائج البحث عن: {context['task_description']}\n\nتم العثور على معلومات قيمة حول الموضوع. يظهر أن هناك العديد من المصادر الموثوقة التي تشير إلى أهمية هذا المجال. وفقًا للدراسات الحديثة، يمكن تحديد عدة اتجاهات رئيسية في هذا المجال."
            else:
                return "تم إجراء البحث وجمع المعلومات المطلوبة من مصادر متعددة."
        elif "analyze" in prompt_lower or "تحليل" in prompt_lower:
            return "نتائج التحليل: بناءً على البيانات المتاحة، يمكن استنتاج أن هناك علاقة قوية بين العوامل الرئيسية. تُظهر الاتجاهات نموًا بنسبة 25% في العام الماضي، مع توقعات بزيادة مماثلة في المستقبل القريب."
        elif "summarize" in prompt_lower or "تلخيص" in prompt_lower or "ملخص" in prompt_lower:
            if context and "task_description" in context:
                return f"ملخص النتائج لـ: {context['task_description']}\n\nبعد إجراء البحث والتحليل المتعمق، يمكننا استنتاج عدة نقاط رئيسية: 1) هناك أدلة قوية تدعم الفرضية الأساسية، 2) تظهر البيانات اتجاهًا إيجابيًا مستمرًا، 3) هناك فرص كبيرة للتطوير المستقبلي في هذا المجال. التوصيات: الاستثمار في البحث والتطوير، وتوسيع نطاق التطبيقات، وتعزيز التعاون مع المؤسسات الرائدة."
            else:
                return "ملخص شامل: تم تحقيق الأهداف الرئيسية للمهمة، مع تحديد نقاط القوة والضعف والفرص المستقبلية. النتائج تشير إلى إمكانيات كبيرة للتطوير والنمو."
        else:
            return f"تم معالجة الطلب: {prompt[:50]}... وتم استخلاص المعلومات المطلوبة بنجاح. النتائج تشير إلى استنتاجات مهمة يمكن الاستفادة منها في الخطوات القادمة."
    
    def get_embedding(self, text: str) -> List[float]:
        """توليد تمثيل شعاعي وهمي للنص"""
        # توليد متجه عشوائي ثابت بناءً على تجزئة النص
        text_hash = hashlib.md5(text.encode()).hexdigest()
        seed = int(text_hash, 16) % (2**32)
        random.seed(seed)
        
        # إنشاء متجه 1536-بُعد (مشابه لـ OpenAI embeddings)
        return [random.uniform(-1, 1) for _ in range(1536)]