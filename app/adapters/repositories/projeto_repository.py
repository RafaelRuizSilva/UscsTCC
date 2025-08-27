from app.core.models.projeto import Projeto
from pymysql.err import IntegrityError
from typing import List, Dict

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

    def deletar_por_id(self, id_projeto: int):
        cursor = self.db_conn.cursor()
        query = "DELETE FROM tb_novo_projeto WHERE id_projeto = %s"
        cursor.execute(query, (id_projeto,))
        self.db_conn.commit()
        if cursor.rowcount == 0:
            raise ValueError("Projeto não encontrado.")

    def get_all(self) -> list[dict]:
        cursor = self.db_conn.cursor()
        query = """SELECT id_projeto,
                          titulo_projeto,
                          resumo,
                          B.nome_completo AS orientador,
                          C.campus
                   FROM tb_novo_projeto as A
                   LEFT JOIN tb_cadastro_orientador as B
                   ON A.id_orientador = B.id_orientador
                   LEFT JOIN tb_campus as C
                   ON A.id_campus = C.id_campus
                   """
        cursor.execute(query)
        rows = cursor.fetchall()
        return [{"id_projeto": row[0], "titulo_projeto": row[1], "resumo": row[2],
                 "orientador": row[3], "campus": row[4]} for row in rows]

    # ✅ NOVO: lista apenas do orientador logado
    def listar_por_orientador(self, id_orientador: int, limit: int = 100, offset: int = 0) -> List[Dict]:
        cursor = self.db_conn.cursor()
        try:
            query = """SELECT A.id_projeto,
                              A.titulo_projeto,
                              A.resumo,
                              B.nome_completo AS orientador,
                              C.campus
                       FROM tb_novo_projeto AS A
                       LEFT JOIN tb_cadastro_orientador AS B
                         ON A.id_orientador = B.id_orientador
                       LEFT JOIN tb_campus AS C
                         ON A.id_campus = C.id_campus
                       WHERE A.id_orientador = %s
                       ORDER BY A.id_projeto DESC
                       LIMIT %s OFFSET %s"""
            cursor.execute(query, (id_orientador, limit, offset))
            rows = cursor.fetchall()
            return [{"id_projeto": row[0], "titulo_projeto": row[1], "resumo": row[2],
                     "orientador": row[3], "campus": row[4]} for row in rows]
        finally:
            cursor.close()
