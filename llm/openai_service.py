# مثال مبسط لخدمة OpenAI
import openai
from .llm_service import LLMService

class OpenAIService(LLMService):
    def __init__(self, api_key):
        super().__init__(api_key)
        openai.api_key = api_key
        
    def query(self, prompt, **kwargs):
        """إرسال استعلام إلى OpenAI"""
        model = kwargs.get("model", "gpt-4")
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.7)
        )
        return response.choices[0].message.content