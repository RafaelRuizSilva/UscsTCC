from typing import List, Optional
from pymysql.err import IntegrityError
from app.core.models.orientador import Orientador
from app.core.models.orientador_out import OrientadorOut
from app.core.ports.output.porta_orientador_repository import IOrientadorRepository

class OrientadorRepository(IOrientadorRepository):
    def __init__(self, db_conn):
        self.db_conn = db_conn

    # ---------- CREATE ----------
    def create(self, orientador: Orientador) -> int:
        cursor = self.db_conn.cursor()
        try:
            query = """
                INSERT INTO tb_cadastro_orientador (nome_completo, email, cpf, senha_hash)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (orientador.nome_completo.lower(), orientador.email, orientador.cpf, orientador.senha_hash)
            )
            self.db_conn.commit()
            return cursor.lastrowid

        except IntegrityError as err:
            error_msg = str(err).lower()
            if "duplicate entry" in error_msg and "cpf" in error_msg:
                raise ValueError("CPF já cadastrado.")
            elif "duplicate entry" in error_msg and "email" in error_msg:
                raise ValueError("E-mail já cadastrado.")
            elif "foreign key constraint fails" in error_msg:
                raise ValueError("ID do curso inválido.")
            else:
                raise
        finally:
            cursor.close()

    # ---------- READS ----------
    def listar_todos(self) -> List[OrientadorOut]:
        cursor = self.db_conn.cursor()
        try:
            query = """
                SELECT id_orientador, nome_completo, email, cpf
                FROM tb_cadastro_orientador
                ORDER BY id_orientador DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            return [self._row_to_out(row) for row in rows]
        finally:
            cursor.close()

    def obter_por_id(self, orientador_id: int) -> Optional[OrientadorOut]:
        cursor = self.db_conn.cursor()
        try:
            query = """
                SELECT id_orientador, nome_completo, email, cpf
                FROM tb_cadastro_orientador
                WHERE id_orientador = %s
                LIMIT 1
            """
            cursor.execute(query, (orientador_id,))
            row = cursor.fetchone()
            return self._row_to_out(row) if row else None
        finally:
            cursor.close()

    def obter_por_nome(self, nome: str) -> Optional[OrientadorOut]:
        cursor = self.db_conn.cursor()
        try:
            # Equivalente ao ILIKE (case-insensitive)
            query = """
                SELECT id_orientador, nome_completo, email, cpf
                FROM tb_cadastro_orientador
                WHERE LOWER(nome_completo) LIKE %s
                ORDER BY id_orientador DESC
                LIMIT 1
            """
            like_term = f"%{nome.strip().lower()}%"
            cursor.execute(query, (like_term,))
            row = cursor.fetchone()
            return self._row_to_out(row) if row else None
        finally:
            cursor.close()

    # ---------- Helpers ----------
    def _row_to_out(self, row) -> OrientadorOut:
        # row é uma tupla (id, nome_completo, email, cpf) no cursor padrão do PyMySQL
        return OrientadorOut(
            id=row[0],
            nome_completo=row[1],
            email=row[2],
            cpf=row[3],
        )
