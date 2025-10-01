from app.core.models.projeto import Projeto
from pymysql.err import IntegrityError
from typing import List, Dict, Optional

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
        query = """
            SELECT A.id_projeto,
                   A.titulo_projeto,
                   A.resumo,
                   B.nome_completo AS orientador,
                   C.campus,
                   IF(A.docx_file IS NULL, 0, 1) AS has_docx,  -- 👈 não traz o BLOB
                   IF(A.pdf_file  IS NULL, 0, 1) AS has_pdf    -- 👈 idem
              FROM tb_novo_projeto AS A
         LEFT JOIN tb_cadastro_orientador AS B ON A.id_orientador = B.id_orientador
         LEFT JOIN tb_campus            AS C ON A.id_campus     = C.id_campus
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return [
            {
                "id_projeto": r[0],
                "titulo_projeto": r[1],
                "resumo": r[2],
                "orientador": r[3],
                "campus": r[4],
                "has_docx": bool(r[5]),
                "has_pdf": bool(r[6]),
            }
            for r in rows
        ]

    def listar_por_orientador(self, id_orientador: int, limit: int = 100, offset: int = 0) -> List[Dict]:
        cursor = self.db_conn.cursor()
        try:
            query = """
                SELECT A.id_projeto,
                       A.titulo_projeto,
                       A.resumo,
                       B.nome_completo AS orientador,
                       C.campus,
                       IF(A.docx_file IS NULL, 0, 1) AS has_docx,
                       IF(A.pdf_file  IS NULL, 0, 1) AS has_pdf
                  FROM tb_novo_projeto AS A
             LEFT JOIN tb_cadastro_orientador AS B ON A.id_orientador = B.id_orientador
             LEFT JOIN tb_campus            AS C ON A.id_campus     = C.id_campus
                 WHERE A.id_orientador = %s
              ORDER BY A.id_projeto DESC
                 LIMIT %s OFFSET %s
            """
            cursor.execute(query, (id_orientador, limit, offset))
            rows = cursor.fetchall()
            return [
                {
                    "id_projeto": r[0],
                    "titulo_projeto": r[1],
                    "resumo": r[2],
                    "orientador": r[3],
                    "campus": r[4],
                    "has_docx": bool(r[5]),
                    "has_pdf": bool(r[6]),
                }
                for r in rows
            ]
        finally:
            cursor.close()

    def listar_alunos_por_projeto(self, id_projeto: int) -> List[Dict]:
        cursor = self.db_conn.cursor()
        try:
            query = """
                SELECT a.id_aluno, a.nome_completo, a.email, a.cpf, a.id_curso
                  FROM tb_projeto_aluno pa
                  JOIN tb_cadastro_aluno a ON a.id_aluno = pa.id_aluno
                 WHERE pa.id_projeto = %s
                   AND a.status = 'APROVADO'
              ORDER BY a.nome_completo ASC
            """
            cursor.execute(query, (id_projeto,))
            rows = cursor.fetchall()
            return [
                {"id": r[0], "nome_completo": r[1], "email": r[2], "cpf": r[3], "id_curso": r[4]}
                for r in rows
            ]
        finally:
            cursor.close()

    def update_docx_file(self, id_projeto: int, data: bytes) -> None:
        c = self.db_conn.cursor()
        try:
            c.execute("UPDATE tb_novo_projeto SET docx_file=%s WHERE id_projeto=%s", (data, id_projeto))
            self.db_conn.commit()
            if c.rowcount == 0:
                raise ValueError("Projeto não encontrado.")
        finally:
            c.close()

    def update_pdf_file(self, id_projeto: int, data: bytes) -> None:
        c = self.db_conn.cursor()
        try:
            c.execute("UPDATE tb_novo_projeto SET pdf_file=%s WHERE id_projeto=%s", (data, id_projeto))
            self.db_conn.commit()
            if c.rowcount == 0:
                raise ValueError("Projeto não encontrado.")
        finally:
            c.close()

    def get_docx_file(self, id_projeto: int) -> bytes | None:
        c = self.db_conn.cursor()
        try:
            c.execute("SELECT docx_file FROM tb_novo_projeto WHERE id_projeto=%s", (id_projeto,))
            row = c.fetchone()
            return row[0] if row and row[0] is not None else None
        finally:
            c.close()

    def get_pdf_file(self, id_projeto: int) -> bytes | None:
        c = self.db_conn.cursor()
        try:
            c.execute("SELECT pdf_file FROM tb_novo_projeto WHERE id_projeto=%s", (id_projeto,))
            row = c.fetchone()
            return row[0] if row and row[0] is not None else None
        finally:
            c.close()
