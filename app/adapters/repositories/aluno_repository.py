from app.core.models.aluno import Aluno
from pymysql.err import IntegrityError
from app.core.security import gerar_hash_senha

class AlunoRepository:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create(self, aluno: Aluno) -> int:
        cursor = self.db_conn.cursor()

        try:
            query = """
            INSERT INTO tb_cadastro_aluno (nome_completo, email, cpf, id_curso, senha_hash)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (aluno.nome_completo.lower(), aluno.email,
                                   aluno.cpf, aluno.id_curso, aluno.senha_hash))
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

    def list_all(self) -> list[dict]:
        cursor = self.db_conn.cursor()
        query = """
            SELECT id_aluno, nome_completo, email, cpf, id_curso
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
            }
            for r in rows
        ]

    def get_by_id(self, aluno_id: int) -> dict | None:
        cursor = self.db_conn.cursor()
        query = """
            SELECT id_aluno, nome_completo, email, cpf, id_curso
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
        }


    def delete(self, aluno_id: int) -> None:
        cursor = self.db_conn.cursor()
        query = "DELETE FROM tb_cadastro_aluno WHERE id_aluno = %s"
        cursor.execute(query, (aluno_id,))
        self.db_conn.commit()
        if cursor.rowcount == 0:
            raise ValueError("Aluno não encontrado.")