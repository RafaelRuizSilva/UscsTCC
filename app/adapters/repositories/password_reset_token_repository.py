from typing import Optional, Dict
from datetime import datetime
from app.core.ports.output.porta_password_reset_token_repository import IPasswordResetTokenRepository

class PasswordResetTokenRepository(IPasswordResetTokenRepository):
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create_token(self, user_type: str, user_id: int, token_hash: str, expires_at: datetime) -> int:
        cur = self.db_conn.cursor()
        cur.execute("""
            INSERT INTO tb_password_reset_token (user_type, user_id, token_hash, expires_at)
            VALUES (%s, %s, %s, %s)
        """, (user_type, user_id, token_hash, expires_at))
        self.db_conn.commit()
        return cur.lastrowid

    def get_valid_by_hash(self, token_hash: str) -> Optional[Dict]:
        cur = self.db_conn.cursor()
        cur.execute("""
            SELECT id, user_type, user_id, token_hash, expires_at, used_at, created_at
            FROM tb_password_reset_token
            WHERE token_hash = %s
            LIMIT 1
        """, (token_hash,))
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "user_type": row[1],
            "user_id": row[2],
            "token_hash": row[3],
            "expires_at": row[4],
            "used_at": row[5],
            "created_at": row[6],
        }

    def mark_used(self, token_id: int) -> None:
        cur = self.db_conn.cursor()
        cur.execute("""
            UPDATE tb_password_reset_token
               SET used_at = NOW()
             WHERE id = %s
        """, (token_id,))
        self.db_conn.commit()
