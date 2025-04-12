import aiosqlite
from data import CREATOR_ID, ADMIN_ID

class DatabaseManager:
    def __init__(self, db_path='bot.db'):
        self.db_path = db_path
        self.conn = None

    async def connect(self):
        self.conn = await aiosqlite.connect(self.db_path)
        await self._create_tables()

    async def _create_tables(self):
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                tg_id INTEGER UNIQUE,
                level INTEGER DEFAULT 1,
                message_count INTEGER DEFAULT 0
            )
        ''')
        await self.conn.commit()

    async def close(self):
        if self.conn:
            await self.conn.close()

    async def insert(self, name: str, tg_id: int):
        try:
            # Определяем уровень доступа
            level = 2 if tg_id in (ADMIN_ID, CREATOR_ID) else 1
            
            await self.conn.execute(
                "INSERT INTO users (name, tg_id, level) VALUES (?, ?, ?)",
                (name, tg_id, level)  # Добавляем уровень в запрос
            )
            await self.conn.commit()
            return True
        except aiosqlite.IntegrityError:
            return False

    async def get_user(self, tg_id: int):
        cursor = await self.conn.execute(
            "SELECT * FROM users WHERE tg_id = ?", 
            (tg_id,))
        return await cursor.fetchone()

    async def increment_message_count(self, tg_id: int):
        await self.conn.execute(
            "UPDATE users SET message_count = message_count + 1 WHERE tg_id = ?",
            (tg_id,))
        await self.conn.commit()

    async def get_all_users(self):
        cursor = await self.conn.execute("SELECT * FROM users")
        return await cursor.fetchall()

    async def get_users_by_level(self, level: int):
        cursor = await self.conn.execute(
            "SELECT * FROM users WHERE level = ?",
            (level,))
        return await cursor.fetchall()

    async def update_user_level(self, tg_id: int, new_level: int):
        await self.conn.execute(
            "UPDATE users SET level = ? WHERE tg_id = ?",
            (new_level, tg_id))
        await self.conn.commit()