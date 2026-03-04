import aiosqlite
import json
from datetime import datetime
from config import DATABASE_PATH


class DBManager:
    def __init__(self):
        self.db_path = DATABASE_PATH

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    communication_style TEXT DEFAULT 'conversational',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    role TEXT,
                    content TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS memory_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    note TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS task_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    task_type TEXT,
                    description TEXT,
                    status TEXT,
                    result TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS automations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    task TEXT,
                    schedule TEXT,
                    active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

    async def get_or_create_user(self, user_id, username, first_name):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
                user = await cursor.fetchone()
            if not user:
                await db.execute(
                    "INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
                    (user_id, username, first_name)
                )
                await db.commit()

    async def get_user_style(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT communication_style FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else "conversational"

    async def set_user_style(self, user_id, style):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET communication_style = ? WHERE user_id = ?",
                (style, user_id)
            )
            await db.commit()

    async def add_message(self, user_id, role, content):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO conversations (user_id, role, content) VALUES (?, ?, ?)",
                (user_id, role, content)
            )
            await db.commit()

    async def get_conversation_history(self, user_id, limit=50):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT role, content FROM conversations WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit)
            ) as cursor:
                rows = await cursor.fetchall()
                return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

    async def clear_history(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM conversations WHERE user_id = ?", (user_id,))
            await db.commit()

    async def add_memory_note(self, user_id, note):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO memory_notes (user_id, note) VALUES (?, ?)",
                (user_id, note)
            )
            await db.commit()

    async def get_memory_notes(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, note, created_at FROM memory_notes WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            ) as cursor:
                return await cursor.fetchall()

    async def clear_memory_notes(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM memory_notes WHERE user_id = ?", (user_id,))
            await db.commit()

    async def add_task(self, user_id, task_type, description, status, result=""):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO task_history (user_id, task_type, description, status, result) VALUES (?, ?, ?, ?, ?)",
                (user_id, task_type, description, status, result)
            )
            await db.commit()

    async def get_task_history(self, user_id, limit=10):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT task_type, description, status, created_at FROM task_history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit)
            ) as cursor:
                return await cursor.fetchall()

    async def add_automation(self, user_id, name, task, schedule):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO automations (user_id, name, task, schedule) VALUES (?, ?, ?, ?)",
                (user_id, name, task, schedule)
            )
            await db.commit()
            async with db.execute("SELECT last_insert_rowid()") as cursor:
                row = await cursor.fetchone()
                return row[0]

    async def get_automations(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, name, task, schedule, active FROM automations WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                return await cursor.fetchall()

    async def get_all_active_automations(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, user_id, name, task, schedule FROM automations WHERE active = 1"
            ) as cursor:
                return await cursor.fetchall()
