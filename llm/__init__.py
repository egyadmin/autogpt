"""
وحدة نماذج اللغة الكبيرة (LLM)
============================
توفر هذه الوحدة واجهات للتفاعل مع نماذج اللغة المختلفة.
"""

from .llm_service import LLMService
from .mock_service import MockLLMService

# تصدير الواجهات الأساسية للاستخدام المباشر
__all__ = ['LLMService', 'MockLLMService']

# محاولة استيراد الخدمات المتاحة وتصديرها إذا كانت موجودة
try:
    from .openai_service import OpenAIService
    __all__.append('OpenAIService')
except ImportError:
    pass

try:
    from .anthropic_service import AnthropicService
    __all__.append('AnthropicService')
except ImportError:
    pass

try:
    from .llama_service import LlamaService
    __all__.append('LlamaService')
except ImportError:
    pass