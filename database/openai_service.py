# مثال مبسط لفئة DatabaseService
class DatabaseService:
    def save_agent(self, agent):
        """حفظ بيانات الوكيل"""
        raise NotImplementedError
        
    def get_agent(self, agent_id):
        """استرجاع بيانات وكيل محدد"""
        raise NotImplementedError