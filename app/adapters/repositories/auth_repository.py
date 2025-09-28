from typing import Optional, Dict
from app.core.ports.output.porta_auth_repository import IAuthRepository

class AuthRepository(IAuthRepository):
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def find_account_by_email(self, email: str) -> Optional[Dict]:
        cur = self.db_conn.cursor()

        # 1) aluno
        cur.execute("""
            SELECT id_aluno, nome_completo, email
            FROM tb_cadastro_aluno
            WHERE email = %s
            LIMIT 1
        """, (email,))
        row = cur.fetchone()
        if row:
            return {"id": row[0], "nome_completo": row[1], "email": row[2], "user_type": "aluno"}

        # 2) orientador
        cur.execute("""
            SELECT id_orientador, nome_completo, email
            FROM tb_cadastro_orientador
            WHERE email = %s
            LIMIT 1
        """, (email,))
        row = cur.fetchone()
        if row:
            return {"id": row[0], "nome_completo": row[1], "email": row[2], "user_type": "orientador"}

        # 3) secretaria (se existir)
        try:
            cur.execute("""
                SELECT id_secretaria, nome_completo, email
                FROM tb_cadastro_secretaria
                WHERE email = %s
                LIMIT 1
            """, (email,))
            row = cur.fetchone()
            if row:
                return {"id": row[0], "nome_completo": row[1], "email": row[2], "user_type": "secretaria"}
        except Exception:
            pass  # tabela pode não existir em alguns ambientes

        return None

    def update_password_hash(self, user_type: str, user_id: int, senha_hash: str) -> None:
        cur = self.db_conn.cursor()
        if user_type == "aluno":
            cur.execute("UPDATE tb_cadastro_aluno SET senha_hash=%s WHERE id_aluno=%s", (senha_hash, user_id))
        elif user_type == "orientador":
            cur.execute("UPDATE tb_cadastro_orientador SET senha_hash=%s WHERE id_orientador=%s", (senha_hash, user_id))
        elif user_type == "secretaria":
            cur.execute("UPDATE tb_cadastro_secretaria SET senha_hash=%s WHERE id_secretaria=%s", (senha_hash, user_id))
        else:
            raise ValueError("Tipo de usuário inválido")

        self.db_conn.commit()
        if cur.rowcount == 0:
            raise ValueError("Usuário não encontrado")
