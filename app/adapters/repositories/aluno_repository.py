from app.core.models.aluno import Aluno
from pymysql.err import IntegrityError

class AlunoRepository:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create(self, aluno: Aluno, pdf_bytes: bytes) -> int:
        cursor = self.db_conn.cursor()
        try:
            query = """
                INSERT INTO tb_cadastro_aluno
                    (nome_completo, email, cpf, id_curso, possui_trabalho_remunerado, senha_hash, status, pdf_file)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (
                    aluno.nome_completo.lower(), aluno.email, aluno.cpf,
                    aluno.id_curso, aluno.possui_trabalho_remunerado,
                    aluno.senha_hash, "PENDENTE", pdf_bytes
                )
            )
            self.db_conn.commit()
            return cursor.lastrowid
        except IntegrityError as err:
            msg = str(err).lower()
            if "duplicate entry" in msg and "cpf" in msg:
                raise ValueError("CPF já cadastrado.")
            elif "duplicate entry" in msg and "email" in msg:
                raise ValueError("E-mail já cadastrado.")
            elif "foreign key constraint fails" in msg:
                raise ValueError("ID do curso inválido.")
            else:
                raise
        finally:
            cursor.close()

    def list_all(self) -> list[dict]:
        cursor = self.db_conn.cursor()
        try:
            query = """
                SELECT id_aluno, nome_completo, email, cpf, id_curso, possui_trabalho_remunerado, status,
                       IF(pdf_file IS NULL, 0, 1) AS has_pdf
                  FROM tb_cadastro_aluno
              ORDER BY nome_completo ASC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            return [
                {
                    "id": r[0],
                    "nome_completo": r[1],
                    "email": r[2],
                    "cpf": r[3],
                    "id_curso": r[4],
                    "possui_trabalho_remunerado": r[5],
                    "status": r[6],
                    "has_pdf": bool(r[7]),
                }
                for r in rows
            ]
        finally:
            cursor.close()

    def get_by_id(self, aluno_id: int) -> dict | None:
        cursor = self.db_conn.cursor()
        try:
            query = """
                SELECT id_aluno, nome_completo, email, cpf, id_curso, possui_trabalho_remunerado, status,
                       IF(pdf_file IS NULL, 0, 1) AS has_pdf
                  FROM tb_cadastro_aluno
                 WHERE id_aluno = %s
            """
            cursor.execute(query, (aluno_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row[0],
                "nome_completo": row[1],
                "email": row[2],
                "cpf": row[3],
                "id_curso": row[4],
                "possui_trabalho_remunerado": row[5],
                "status": row[6],
                "has_pdf": bool(row[7]),
            }
        finally:
            cursor.close()

    def delete(self, aluno_id: int) -> None:
        cursor = self.db_conn.cursor()
        try:
            cursor.execute("DELETE FROM tb_cadastro_aluno WHERE id_aluno = %s", (aluno_id,))
            self.db_conn.commit()
            if cursor.rowcount == 0:
                raise ValueError("Aluno não encontrado.")
        finally:
            cursor.close()

    def update_status(self, aluno_id: int, novo_status: str) -> None:
        cursor = self.db_conn.cursor()
        try:
            cursor.execute("UPDATE tb_cadastro_aluno SET status = %s WHERE id_aluno = %s", (novo_status, aluno_id))
            self.db_conn.commit()
            if cursor.rowcount == 0:
                raise ValueError("Aluno não encontrado.")
        finally:
            cursor.close()

    # download
    def get_pdf_by_id(self, aluno_id: int) -> bytes | None:
        cursor = self.db_conn.cursor()
        try:
            cursor.execute("SELECT pdf_file FROM tb_cadastro_aluno WHERE id_aluno = %s", (aluno_id,))
            row = cursor.fetchone()
            return row[0] if row and row[0] is not None else None
        finally:
            cursor.close()