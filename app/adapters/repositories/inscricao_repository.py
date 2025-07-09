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
