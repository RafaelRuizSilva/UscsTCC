from app.core.models.projeto import Projeto
from pymysql.err import IntegrityError

class ProjetoRepository:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create(self, projeto: Projeto) -> int:
        cursor = self.db_conn.cursor()

        try:
            query = """INSERT INTO tb_novo_projeto(titulo_projeto,
                                                   resumo,
                                                   id_orientador,
                                                   id_campus) 
                       VALUES (%s, %s, %s, %s)"""

            cursor.execute(query, (projeto.titulo_projeto, projeto.resumo,
                                   projeto.id_orientador, projeto.id_campus))
            self.db_conn.commit()
            return cursor.lastrowid
        except IntegrityError as err:
            error_msg = str(err).lower()
            if "foreign key constraint fails" in error_msg:
                raise ValueError("ID do orientador e/ou ID do campus inválido(s).")