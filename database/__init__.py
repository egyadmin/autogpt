"""
وحدة قواعد البيانات (DATABASE)
=======================
توفر هذه الوحدة خدمات تخزين واسترجاع البيانات للنظام.
"""

from .db_service import DatabaseService
from .memory_db import MemoryDatabaseService

__all__ = ['DatabaseService', 'MemoryDatabaseService']

# محاولة استيراد خدمات قواعد البيانات الأخرى وتصديرها إذا كانت موجودة
try:
    from .sqlite_db import SQLiteDatabaseService
    __all__.append('SQLiteDatabaseService')
except ImportError:
    pass

try:
    from .mongo_db import MongoDatabaseService
    __all__.append('MongoDatabaseService')
except ImportError:
    pass