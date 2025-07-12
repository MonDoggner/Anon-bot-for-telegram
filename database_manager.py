import asyncio
import aiosqlite


class DatabaseManager:
    def __init__(self):
        asyncio.run(self.initialize())

    @staticmethod
    async def initialize():
        """Асинхронная инициализация базы данных"""
        async with aiosqlite.connect('bot.db') as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    username TEXT
                )
            ''')
            await db.commit()

    @staticmethod
    async def add_user(user_id: int, username: str):
        async with aiosqlite.connect('bot.db') as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
                (user_id, username or '')
            )
            await db.commit()
