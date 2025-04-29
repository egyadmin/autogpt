"""
وحدة الأدوات (TOOLS)
===============
توفر هذه الوحدة مجموعة من الأدوات المساعدة للوكلاء.
"""

from tools.tool import Tool

# قائمة بجميع الأدوات المتاحة
__all__ = ['Tool']

# محاولة استيراد الأدوات المتاحة وتصديرها إذا كانت موجودة
tool_classes = [
    'WebSearchTool',
    'WebScrapingTool',
    'FileOperationsTool',
    'DataAnalysisTool',
    'ContentGeneratorTool'
]

# استيراد الأدوات المتاحة ديناميكياً
for tool_name in tool_classes:
    try:
        module_name = tool_name.lower()
        if module_name.endswith('tool'):
            module_name = module_name[:-4]
        module_path = f"tools.{module_name}"
        module = __import__(module_path, globals(), locals(), [tool_name], 0)
        tool_class = getattr(module, tool_name)
        globals()[tool_name] = tool_class
        __all__.append(tool_name)
    except (ImportError, AttributeError) as e:
        # تجاهل الأدوات غير الموجودة
        pass