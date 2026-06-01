import os
import sqlite3
from typing import Optional, Dict
from werkzeug.security import generate_password_hash, check_password_hash

class AuthManager:
    def __init__(self, db_path: str = "auth.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True) if os.path.dirname(self.db_path) else None
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    role TEXT DEFAULT 'user'
                )
            """)
            # Se não houver usuários, criar um admin padrão (somente ambiente de desenvolvimento)
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                self.create_user('admin', 'admin', full_name='Administrator', role='admin')
            conn.commit()

    def create_user(self, username: str, password: str, full_name: str = '', role: str = 'user') -> int:
        password_hash = generate_password_hash(password)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                               (username, password_hash, full_name, role))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # usuário existe — atualizar senha e dados
                cursor.execute("UPDATE users SET password_hash = ?, full_name = ?, role = ? WHERE username = ?",
                               (password_hash, full_name, role, username))
                conn.commit()
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                row = cursor.fetchone()
                return row[0] if row else 0

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, full_name, role FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def verify_password(self, username: str, password: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if not row:
                return False
            return check_password_hash(row['password_hash'], password)
