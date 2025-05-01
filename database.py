import sqlite3
import os
from typing import Dict

class Database:
    def __init__(self, db_name: str = "DATABASE.db"):
        self.db_path = os.path.join(os.path.dirname(__file__), db_name)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Возвращает соединение с БД."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Инициализирует таблицы, если они не существуют."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    sends INTEGER DEFAULT 0
                )
            ''')
            
            # Таблица админов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    level INTEGER
                )
            ''')
            
            # Начальные данные
            cursor.executemany(
                'INSERT OR IGNORE INTO admins VALUES (?, ?, ?)',
                [(1, 1089008595, 2), (2, 1244819972, 1)]
            )
            cursor.execute('INSERT OR IGNORE INTO users VALUES (1, 1089008595, 0)')
            conn.commit()

    def increment_user_sends(self, user_id: int) -> None:
        """Увеличивает счётчик отправленных сообщений пользователя."""
        with self._get_connection() as conn:
            conn.execute(
                'UPDATE users SET sends = sends + 1 WHERE user_id = ?',
                (user_id,)
            )
            conn.commit()

    def get_stats(self) -> Dict[str, int]:
        """Возвращает статистику: общее число пользователей и сообщений."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            cursor.execute('SELECT SUM(sends) FROM users')
            total_messages = cursor.fetchone()[0] or 0
            return {
                'total_users': total_users,
                'total_messages': total_messages
            }

    def is_admin(self, user_id: int) -> bool:
        """Проверяет, является ли пользователь админом."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM admins WHERE user_id = ?', (user_id,))
            return cursor.fetchone() is not None