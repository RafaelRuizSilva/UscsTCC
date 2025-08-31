from typing import Optional, List, Dict
from pymysql.err import IntegrityError
from app.core.models.secretaria import Secretaria
from app.core.ports.output.porta_secretaria_repository import ISecretariaRepository

class SecretariaRepository(ISecretariaRepository):
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create(self, secretaria: Secretaria) -> int:
        cursor = self.db_conn.cursor()
        try:
            query = """
                INSERT INTO tb_cadastro_secretaria (nome_completo, email, cpf, senha_hash)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (secretaria.nome_completo.lower(), secretaria.email, secretaria.cpf, secretaria.senha_hash)
            )
            self.db_conn.commit()
            return cursor.lastrowid
        except IntegrityError as err:
            error_msg = str(err).lower()
            if "duplicate entry" in error_msg and "cpf" in error_msg:
                raise ValueError("CPF já cadastrado.")
            elif "duplicate entry" in error_msg and "email" in error_msg:
                raise ValueError("E-mail já cadastrado.")
            else:
                raise
        finally:
            cursor.close()

    def get_by_email(self, email: str) -> Optional[Dict]:
        cursor = self.db_conn.cursor()
        try:
            query = """
                SELECT id_secretaria, nome_completo, email, cpf, senha_hash
                FROM tb_cadastro_secretaria
                WHERE email = %s
                LIMIT 1
            """
            cursor.execute(query, (email,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row[0],
                "nome_completo": row[1],
                "email": row[2],
                "cpf": row[3],
                "senha_hash": row[4],
            }
        finally:
            cursor.close()