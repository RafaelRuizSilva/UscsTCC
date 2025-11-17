from app.core.models.projeto import Projeto
from pymysql.err import IntegrityError
from typing import List, Dict, Optional
import base64

class ProjetoRepository:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create(self, projeto: Projeto) -> int:
        cursor = self.db_conn.cursor()
        try:
            # ⬇️ decodifica o Base64 vindo do model
            try:
                ideia_bytes = base64.b64decode(projeto.ideia_inicial_b64, validate=True)
            except Exception:
                raise ValueError("ideia_inicial_b64 inválido (Base64).")
            if not ideia_bytes:
                raise ValueError("Arquivo DOCX 'ideia_incicial' vazio.")

            cursor.execute(
                """
                INSERT INTO tb_novo_projeto
                    (cod_projeto, titulo_projeto, resumo, ideia_inicial, id_orientador, id_campus)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (projeto.cod_projeto,
                 projeto.titulo_projeto,
                 projeto.resumo,
                 ideia_bytes,                 # ⬅️ grava no BLOB
                 projeto.id_orientador,
                 projeto.id_campus),
            )
            self.db_conn.commit()
            return cursor.lastrowid
        except IntegrityError as err:
            if "foreign key constraint fails" in str(err).lower():
                raise ValueError("ID do orientador e/ou ID do campus inválido(s).")
            raise
        finally:
            cursor.close()

    def deletar_por_id(self, id_projeto: int):
        cursor = self.db_conn.cursor()
        try:
            cursor.execute("DELETE FROM tb_novo_projeto WHERE id_projeto = %s", (id_projeto,))
            self.db_conn.commit()
            if cursor.rowcount == 0:
                raise ValueError("Projeto não encontrado.")
        finally:
            cursor.close()

    def get_all(self) -> list[dict]:
        cursor = self.db_conn.cursor()
        try:
            cursor.execute(
                """
                SELECT A.id_projeto,
                       A.cod_projeto,
                       A.titulo_projeto,
                       A.resumo,
                       A.id_orientador,
                       B.nome_completo AS orientador,
                       B.email         AS orientador_email,
                       A.id_campus,
                       C.campus,
                       IF(A.ideia_inicial IS NULL, 0, 1) AS has_ideia_inicial,
                       IF(A.docx_file     IS NULL, 0, 1) AS has_docx,
                       IF(A.pdf_file      IS NULL, 0, 1) AS has_pdf,
                       (SELECT COUNT(*) FROM tb_projeto_aluno pa WHERE pa.id_projeto = A.id_projeto) AS total_inscritos
                  FROM tb_novo_projeto AS A
             LEFT JOIN tb_cadastro_orientador AS B ON A.id_orientador = B.id_orientador
             LEFT JOIN tb_campus            AS C ON A.id_campus     = C.id_campus
                """
            )
            rows = cursor.fetchall()
            return [
                {
                    "id_projeto": r[0],
                    "cod_projeto": r[1],
                    "titulo_projeto": r[2],
                    "resumo": r[3],
                    "id_orientador": r[4],
                    "orientador": r[5],
                    "orientador_email": r[6],
                    "id_campus": r[7],
                    "campus": r[8],
                    "has_ideia_inicial": bool(r[9]),  # ⬅️ novo flag
                    "has_docx": bool(r[10]),
                    "has_pdf": bool(r[11]),
                    "total_inscritos": int(r[12] or 0),
                }
                for r in rows
            ]
        finally:
            cursor.close()

    def listar_por_orientador(self, id_orientador: int, limit: int = 100, offset: int = 0) -> List[Dict]:
        cursor = self.db_conn.cursor()
        try:
            cursor.execute(
                """
                SELECT A.id_projeto,
                       A.cod_projeto,
                       A.titulo_projeto,
                       A.resumo,
                       B.nome_completo AS orientador,
                       C.campus,
                       IF(A.ideia_inicial IS NULL, 0, 1) AS has_ideia_inicial,
                       IF(A.docx_file     IS NULL, 0, 1) AS has_docx,
                       IF(A.pdf_file      IS NULL, 0, 1) AS has_pdf
                  FROM tb_novo_projeto AS A
             LEFT JOIN tb_cadastro_orientador AS B ON A.id_orientador = B.id_orientador
             LEFT JOIN tb_campus            AS C ON A.id_campus     = C.id_campus
                 WHERE A.id_orientador = %s
              ORDER BY A.id_projeto DESC
                 LIMIT %s OFFSET %s
                """,
                (id_orientador, limit, offset),
            )
            rows = cursor.fetchall()
            return [
                {
                    "id_projeto": r[0],
                    "cod_projeto": r[1],
                    "titulo_projeto": r[2],
                    "resumo": r[3],
                    "orientador": r[4],
                    "campus": r[5],
                    "has_ideia_inicial": bool(r[6]),  # ⬅️ novo flag
                    "has_docx": bool(r[7]),
                    "has_pdf": bool(r[8]),
                }
                for r in rows
            ]
        finally:
            cursor.close()

    def listar_alunos_por_projeto(self, id_projeto: int) -> List[Dict]:
        cursor = self.db_conn.cursor()
        try:
            cursor.execute(
                """
                SELECT a.id_aluno,
                       a.nome_completo,
                       a.email,
                       a.possui_trabalho_remunerado
                  FROM tb_projeto_aluno pa
                  JOIN tb_cadastro_aluno a ON a.id_aluno = pa.id_aluno
                 WHERE pa.id_projeto = %s
              ORDER BY a.nome_completo ASC
                """,
                (id_projeto,),
            )
            rows = cursor.fetchall()
            return [
                {
                    "id_aluno": r[0],
                    "nome_completo": r[1],
                    "email": r[2],
                    "possuiTrabalhoRemunerado": bool(r[3]),
                }
                for r in rows
            ]
        finally:
            cursor.close()

    # arquivos existentes
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

    # ⬇️ novos helpers para 'ideia_incicial' (DOCX obrigatório no create, mas atualizável depois)
    def update_ideia_incicial_file(self, id_projeto: int, data: bytes) -> None:
        if not data:
            raise ValueError("Arquivo DOCX inválido.")
        c = self.db_conn.cursor()
        try:
            c.execute("UPDATE tb_novo_projeto SET ideia_inicial=%s WHERE id_projeto=%s", (data, id_projeto))
            self.db_conn.commit()
            if c.rowcount == 0:
                raise ValueError("Projeto não encontrado.")
        finally:
            c.close()

    def get_ideia_incicial_file(self, id_projeto: int) -> bytes | None:
        c = self.db_conn.cursor()
        try:
            c.execute("SELECT ideia_inicial FROM tb_novo_projeto WHERE id_projeto=%s", (id_projeto,))
            row = c.fetchone()
            return row[0] if row and row[0] is not None else None
        finally:
            c.close()

    def get_meta_e_pdf(self, id_projeto: int):
        cur = self.db_conn.cursor()
        try:
            cur.execute(
                """
                SELECT titulo_projeto, pdf_file
                  FROM tb_novo_projeto
                 WHERE id_projeto = %s
                 LIMIT 1
                """,
                (id_projeto,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return {"titulo": row[0], "pdf": row[1]}
        finally:
            cur.close()

    def get_by_id(self, id_projeto: int) -> Optional[Dict]:
        c = self.db_conn.cursor()
        try:
            c.execute(
                """
                SELECT id_projeto, cod_projeto, titulo_projeto, resumo, id_orientador, id_campus
                  FROM tb_novo_projeto
                 WHERE id_projeto = %s
                 LIMIT 1
                """,
                (id_projeto,),
            )
            r = c.fetchone()
            if not r:
                return None
            return {
                "id_projeto": r[0],
                "cod_projeto": r[1],
                "titulo_projeto": r[2],
                "resumo": r[3],
                "id_orientador": r[4],
                "id_campus": r[5],
            }
        finally:
            c.close()

    def salvar_envio_avaliadores(self, id_projeto: int, destinatarios: list) -> None:
        cursor = self.db_conn.cursor()

        # Passo 1: Obter os IDs dos avaliadores com base nos e-mails
        query = """
            SELECT id_avaliador, email FROM TB_AVALIADOR_EXTERNO WHERE email IN (%s)
        """
        # Gerar a string do IN para o número de destinatários
        format_strings = ','.join(['%s'] * len(destinatarios))
        query = query % format_strings

        cursor.execute(query, destinatarios)
        avaliadores = cursor.fetchall()

        if not avaliadores:
            raise ValueError("Nenhum avaliador encontrado com os e-mails fornecidos.")

        # Passo 2: Inserir os envios de avaliadores para o projeto
        query_insert = """
            INSERT INTO tb_envio_avaliadores (id_projeto, id_avaliador)
            VALUES (%s, %s)
        """

        # Criação da lista de tuplas com os valores (id_projeto, id_avaliador)
        values = [(id_projeto, avaliador[0]) for avaliador in avaliadores]

        cursor.executemany(query_insert, values)
        self.db_conn.commit()

        # Fechar o cursor após a operação
        cursor.close()

    def get_all_envios(self) -> list:
        cursor = self.db_conn.cursor()
        query = """
            SELECT ea.id_envio, ea.data_envio, a.nome, p.titulo_projeto
            FROM tb_envio_avaliadores ea
            INNER JOIN TB_AVALIADOR_EXTERNO a ON ea.id_avaliador = a.id_avaliador
            INNER JOIN tb_novo_projeto p ON ea.id_projeto = p.id_projeto
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return [
            {
                "id_envio": row[0],
                "data_envio": row[1],
                "avaliador_nome": row[2],
                "titulo_projeto": row[3],
            }
            for row in rows
        ]

    def get_envio_by_id(self, id_envio: int) -> dict:
        cursor = self.db_conn.cursor()
        query = """
            SELECT ea.id_envio, ea.data_envio, a.nome, p.titulo_projeto
            FROM tb_envio_avaliadores ea
            INNER JOIN TB_AVALIADOR_EXTERNO a ON ea.id_avaliador = a.id_avaliador
            INNER JOIN tb_novo_projeto p ON ea.id_projeto = p.id_projeto
            WHERE ea.id_envio = %s
        """
        cursor.execute(query, (id_envio,))
        row = cursor.fetchone()
        if row:
            return {
                "id_envio": row[0],
                "data_envio": row[1],
                "avaliador_nome": row[2],
                "titulo_projeto": row[3],
            }
        return None