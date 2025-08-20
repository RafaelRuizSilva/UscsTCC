from app.core.ports.output.porta_inscricao_repository import IInscricaoRepository
from pymysql.err import IntegrityError


class InscricaoRepository(IInscricaoRepository):
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create(self, id_aluno: int, id_projeto: int) -> int:
        cursor = self.db_conn.cursor()
        try:
            query = """
            INSERT INTO tb_projeto_aluno (id_aluno, id_projeto)
            VALUES (%s, %s)
            """
            cursor.execute(query, (id_aluno, id_projeto))
            self.db_conn.commit()
            return cursor.lastrowid
        except IntegrityError as err:
            error_msg = str(err).lower()
            if "Duplicate entry" in str(err):
                raise ValueError("Aluno já inscrito neste projeto.")
            elif "foreign key constraint fails" in error_msg:
                raise ValueError("ID do projeto inválido.")

    def list_all(self) -> list[dict]:
        cursor = self.db_conn.cursor()
        query = """
        SELECT id_inscricao, id_aluno, id_projeto
        FROM tb_projeto_aluno
        ORDER BY id_inscricao ASC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return [{"id_inscricao": r[0], "id_aluno": r[1], "id_projeto": r[2]} for r in rows]

    def get_by_id(self, id_inscricao: int) -> dict | None:
        cursor = self.db_conn.cursor()
        query = """
        SELECT id_inscricao, id_aluno, id_projeto
        FROM tb_projeto_aluno
        WHERE id_inscricao = %s
        """
        cursor.execute(query, (id_inscricao,))
        row = cursor.fetchone()
        if not row:
            return None
        return {"id_inscricao": row[0], "id_aluno": row[1], "id_projeto": row[2]}

    def delete(self, id_inscricao: int) -> None:
        cursor = self.db_conn.cursor()
        query = "DELETE FROM tb_projeto_aluno WHERE id_inscricao = %s"
        cursor.execute(query, (id_inscricao,))
        self.db_conn.commit()
        if cursor.rowcount == 0:
            raise ValueError("Inscrição não encontrada.")
