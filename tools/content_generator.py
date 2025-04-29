"""
أداة لإنشاء محتوى متنوع
"""
import json
from typing import List, Dict, Any, Optional
from .tool import Tool

class ContentGeneratorTool(Tool):
    """أداة لإنشاء محتوى متنوع مثل النصوص والمقالات والتقارير"""
    
    def __init__(self):
        super().__init__(
            name="ContentGeneratorTool",
            description="أداة لإنشاء محتوى متنوع مثل النصوص والمقالات والتقارير"
        )
    
    def run(self, query: str, params: Optional[str] = None) -> str:
        """إنشاء محتوى بناءً على المدخلات"""
        try:
            content_type = "general"
            length = "medium"
            tone = "neutral"
            
            if params:
                content_params = json.loads(params)
                content_type = content_params.get("type", content_type)
                length = content_params.get("length", length)
                tone = content_params.get("tone", tone)
                
            return self._generate_content(query, content_type, length, tone)
        
        except Exception as e:
            return f"خطأ في إنشاء المحتوى: {str(e)}"
    
    def _generate_content(self, topic: str, content_type: str, length: str, tone: str) -> str:
        """محاكاة إنشاء محتوى"""
        
        # تعديل طول المحتوى
        if length == "short":
            paragraphs = 2
        elif length == "medium":
            paragraphs = 4
        elif length == "long":
            paragraphs = 8
        else:
            paragraphs = 3
            
        # إنشاء محتوى مختلف حسب النوع
        if content_type == "article":
            return self._generate_article(topic, paragraphs, tone)
        elif content_type == "report":
            return self._generate_report(topic, paragraphs, tone)
        elif content_type == "social_post":
            return self._generate_social_post(topic, tone)
        else:
            return self._generate_general_content(topic, paragraphs, tone)
    
    def _generate_article(self, topic: str, paragraphs: int, tone: str) -> str:
        """إنشاء مقال"""
        title = f"مقال عن: {topic}"
        
        intro = f"مقدمة تناقش أهمية موضوع {topic} وتأثيره على المجالات المختلفة. "
        intro += f"سنتناول في هذا المقال الجوانب المختلفة لـ {topic} مع التركيز على التطورات الحديثة."
        
        body_paragraphs = []
        for i in range(paragraphs - 2):
            body_paragraphs.append(f"فقرة {i+1}: معلومات وتحليلات متعمقة حول {topic}. "
                                  f"تناقش هذه الفقرة جانباً مهماً من جوانب {topic} مع الإشارة إلى الدراسات والأبحاث ذات الصلة.")
            
        conclusion = f"الخلاصة: يتضح مما سبق أهمية {topic} في مجاله. "
        conclusion += f"يمكن الاستفادة من المعلومات المقدمة في هذا المقال لفهم أفضل لـ {topic} والتعامل معه بشكل أكثر فعالية."
        
        article = f"# {title}\n\n{intro}\n\n"
        article += "\n\n".join(body_paragraphs)
        article += f"\n\n{conclusion}"
        
        return article
    
    def _generate_report(self, topic: str, paragraphs: int, tone: str) -> str:
        """إنشاء تقرير"""
        title = f"تقرير عن: {topic}"
        
        executive_summary = f"ملخص تنفيذي: يقدم هذا التقرير تحليلاً شاملاً لـ {topic}. "
        executive_summary += f"يهدف التقرير إلى توفير فهم عميق للموضوع وتقديم توصيات عملية."
        
        sections = []
        sections.append("## المقدمة\n" +
                      f"يتناول هذا التقرير موضوع {topic} وأهميته. " +
                      f"سيتم استعراض الجوانب المختلفة للموضوع مع التركيز على التطبيقات العملية.")
        
        sections.append("## منهجية التقرير\n" +
                      f"تم جمع المعلومات لهذا التقرير من مصادر متنوعة وموثوقة. " +
                      f"تم تحليل البيانات باستخدام أساليب إحصائية مناسبة.")
        
        for i in range(paragraphs - 4):
            sections.append(f"## القسم {i+1}\n" +
                          f"معلومات وتحليلات متعمقة حول جانب محدد من {topic}. " +
                          f"تستند المعلومات إلى بيانات حديثة وتحليلات دقيقة.")
            
        sections.append("## النتائج والتوصيات\n" +
                      f"بناءً على التحليل السابق، يمكن استخلاص النتائج التالية بخصوص {topic}. " +
                      f"كما نقدم مجموعة من التوصيات العملية للتعامل مع الموضوع بشكل أفضل.")
        
        report = f"# {title}\n\n{executive_summary}\n\n"
        report += "\n\n".join(sections)
        
        return report
    
    def _generate_social_post(self, topic: str, tone: str) -> str:
        """إنشاء منشور لوسائل التواصل الاجتماعي"""
        if tone == "formal":
            post = f"إليكم معلومات قيمة حول {topic}. "
            post += f"من المهم الإشارة إلى أن {topic} يلعب دوراً مهماً في مجاله. "
            post += f"نرحب بآرائكم وتعليقاتكم حول هذا الموضوع. #معلومات_مفيدة #{topic.replace(' ', '_')}"
        elif tone == "casual":
            post = f"هل تعرف ما هو {topic}؟ 😃 "
            post += f"إليك بعض المعلومات المثيرة للاهتمام! "
            post += f"شاركنا رأيك في التعليقات 👇 #اعرف_أكثر #{topic.replace(' ', '_')}"
        else:
            post = f"مشاركة معلوماتية عن {topic}. "
            post += f"يعتبر {topic} من المواضيع المهمة التي تستحق الاهتمام. "
            post += f"تابعونا للمزيد من المعلومات المفيدة. #{topic.replace(' ', '_')}"
            
        return post
    
    def _generate_general_content(self, topic: str, paragraphs: int, tone: str) -> str:
        """إنشاء محتوى عام"""
        title = f"معلومات عن: {topic}"
        
        content_paragraphs = []
        for i in range(paragraphs):
            if i == 0:
                content_paragraphs.append(f"مقدمة: {topic} هو موضوع يستحق الدراسة والاهتمام. "
                                         f"سنقدم في هذا المحتوى معلومات مفيدة ومتنوعة حول هذا الموضوع.")
            elif i == paragraphs - 1:
                content_paragraphs.append(f"ختاماً، يمكن القول إن {topic} يمثل جانباً مهماً في مجاله. "
                                         f"المعلومات المقدمة تساعد على فهم أفضل للموضوع واستخدامه بشكل فعال.")
            else:
                content_paragraphs.append(f"معلومات إضافية عن {topic} وكيفية الاستفادة منه. "
                                         f"هناك جوانب متعددة لهذا الموضوع تستحق الاستكشاف والدراسة.")
                
        content = f"# {title}\n\n"
        content += "\n\n".join(content_paragraphs)
        
        return content