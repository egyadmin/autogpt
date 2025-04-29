# مثال مبسط لخدمة SQLite
import sqlite3
from .db_service import DatabaseService

class SQLiteDatabaseService(DatabaseService):
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """إنشاء الجداول إذا لم تكن موجودة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # إنشاء جدول الوكلاء
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            name TEXT,
            goal TEXT,
            description TEXT,
            created_at TEXT,
            data TEXT
        )
        ''')
        
        # إنشاء جدول المهام
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            agent_id TEXT,
            name TEXT,
            description TEXT,
            status TEXT,
            created_at TEXT,
            data TEXT,
            FOREIGN KEY (agent_id) REFERENCES agents (id)
        )
        ''')
        
        conn.commit()
        conn.close()