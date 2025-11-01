from app.core.ports.output.porta_inscricao_repository import IInscricaoRepository
from pymysql.err import IntegrityError

class InscricaoRepository(IInscricaoRepository):
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create(self, id_aluno: int, id_projeto: int) -> int:
        cursor = self.db_conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO tb_inscricao_projeto (id_aluno, id_projeto) VALUES (%s, %s)",
                (id_aluno, id_projeto),
            )
            self.db_conn.commit()
            return cursor.lastrowid
        except IntegrityError as err:
            msg = str(err).lower()
            if "duplicate entry" in msg:
                raise ValueError("Aluno já inscrito neste projeto.")
            if "foreign key constraint fails" in msg:
                raise ValueError("ID de aluno e/ou projeto inválido(s).")
            raise
        finally:
            cursor.close()

    def list_all(self) -> list[dict]:
        cursor = self.db_conn.cursor()
        try:
            cursor.execute(
                """
                SELECT id_inscricao, id_aluno, id_projeto, created_at
                  FROM tb_inscricao_projeto
              ORDER BY id_inscricao ASC
                """
            )
            rows = cursor.fetchall()
            return [
                {"id_inscricao": r[0], "id_aluno": r[1], "id_projeto": r[2], "created_at": r[3].isoformat()}
                for r in rows
            ]
        finally:
            cursor.close()

    def get_by_id(self, id_inscricao: int) -> dict | None:
        cursor = self.db_conn.cursor()
        try:
            cursor.execute(
                """
                SELECT id_inscricao, id_aluno, id_projeto, created_at
                  FROM tb_inscricao_projeto
                 WHERE id_inscricao = %s
                """,
                (id_inscricao,),
            )
            r = cursor.fetchone()
            if not r:
                return None
            return {"id_inscricao": r[0], "id_aluno": r[1], "id_projeto": r[2], "created_at": r[3].isoformat()}
        finally:
            cursor.close()

    def delete(self, id_inscricao: int) -> None:
        cursor = self.db_conn.cursor()
        try:
            cursor.execute("DELETE FROM tb_inscricao_projeto WHERE id_inscricao = %s", (id_inscricao,))
            self.db_conn.commit()
            if cursor.rowcount == 0:
                raise ValueError("Inscrição não encontrada.")
        finally:
            cursor.close()

    # ✅ SECRETARIA: inscrições de um projeto, com dados do aluno
    def list_by_projeto(self, id_projeto: int) -> list[dict]:
        cursor = self.db_conn.cursor()
        try:
            cursor.execute(
                """
                SELECT i.id_inscricao,
                       a.id_aluno,
                       a.nome_completo,
                       a.email,
                       a.cpf,
                       a.possui_trabalho_remunerado,
                       a.status,
                       i.created_at
                  FROM tb_inscricao_projeto i
                  JOIN tb_cadastro_aluno a ON a.id_aluno = i.id_aluno
                 WHERE i.id_projeto = %s
              ORDER BY i.created_at DESC
                """,
                (id_projeto,),
            )
            rows = cursor.fetchall()
            return [
                {
                    "id_inscricao": r[0],
                    "id_aluno": r[1],
                    "nome_aluno": r[2],
                    "email": r[3],
                    "cpf": r[4],
                    "possui_trabalho_remunerado": bool(r[5]),
                    "status_aluno": r[6],
                    "created_at": r[7].isoformat() if r[7] else None,
                }
                for r in rows
            ]
        finally:
            cursor.close()
