from app.core.models.projeto import Projeto
from pymysql.err import IntegrityError
from typing import List, Dict, Optional
import base64

class ProjetoRepository:

    MAX_LIMIT = 200

    def __init__(self, db_conn):
        self.db_conn = db_conn

    # CREATE: agora grava DOCX (ideia_inicial) e PDF (ideia_inicial_pdf)
    def create(self, projeto: Projeto) -> int:
        cursor = self.db_conn.cursor()
        try:
            # DOCX (obrigatório)
            try:
                ideia_docx_bytes = base64.b64decode(projeto.ideia_inicial_b64, validate=True)
            except Exception:
                raise ValueError("ideia_inicial_b64 inválido (Base64).")
            if not ideia_docx_bytes:
                raise ValueError("Arquivo DOCX 'ideia_inicial' vazio.")

            # PDF (obrigatório)
            try:
                ideia_pdf_bytes = base64.b64decode(projeto.ideia_inicial_pdf_b64, validate=True)
            except Exception:
                raise ValueError("ideia_inicial_pdf_b64 inválido (Base64).")
            if not ideia_pdf_bytes:
                raise ValueError("Arquivo PDF 'ideia_inicial_pdf' vazio.")

            cursor.execute(
                """
                INSERT INTO tb_novo_projeto
                    (cod_projeto, titulo_projeto, resumo, ideia_inicial, ideia_inicial_pdf, id_orientador, id_campus, concluido)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    projeto.cod_projeto,
                    projeto.titulo_projeto,
                    projeto.resumo,
                    ideia_docx_bytes,
                    ideia_pdf_bytes,
                    projeto.id_orientador,
                    projeto.id_campus,
                    False  # Por padrão, o projeto começa como não concluído
                ),
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

    def _clamp_limit(self, limit: int) -> int:
        try:
            l = int(limit)
        except Exception:
            l = 50
        if l < 1: l = 1
        if l > self.MAX_LIMIT: l = self.MAX_LIMIT
        return l

    def get_all(self, limit: int = 50, offset: int = 0) -> Dict:
        limit = self._clamp_limit(limit)
        try:
            offset = max(0, int(offset))
        except Exception:
            offset = 0

        cur = self.db_conn.cursor()
        try:
            # total
            cur.execute("SELECT COUNT(*) FROM tb_novo_projeto")
            total = int(cur.fetchone()[0] or 0)

            # page
            cur.execute(
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
                       IF(A.ideia_inicial           IS NULL, 0, 1) AS has_ideia_inicial,
                       IF(A.ideia_inicial_pdf       IS NULL, 0, 1) AS has_ideia_inicial_pdf,
                       IF(A.mon_parcial_docx_file   IS NULL, 0, 1) AS has_mon_parcial_docx,
                       IF(A.mon_parcial_pdf_file    IS NULL, 0, 1) AS has_mon_parcial_pdf,
                       IF(A.mon_final_docx_file     IS NULL, 0, 1) AS has_mon_final_docx,
                       IF(A.mon_final_pdf_file      IS NULL, 0, 1) AS has_mon_final_pdf,
                       A.concluido,
                       (SELECT COUNT(*) FROM tb_projeto_aluno pa WHERE pa.id_projeto = A.id_projeto) AS total_inscritos
                  FROM tb_novo_projeto AS A
             LEFT JOIN tb_cadastro_orientador AS B ON A.id_orientador = B.id_orientador
             LEFT JOIN tb_campus               AS C ON A.id_campus     = C.id_campus
                  ORDER BY A.id_projeto DESC
                     LIMIT %s OFFSET %s
                """,
                (limit, offset),
            )
            rows = cur.fetchall()
            items = [
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
                    "has_ideia_inicial": bool(r[9]),
                    "has_ideia_inicial_pdf": bool(r[10]),
                    "has_mon_parcial_docx": bool(r[11]),
                    "has_mon_parcial_pdf": bool(r[12]),
                    "has_mon_final_docx": bool(r[13]),
                    "has_mon_final_pdf": bool(r[14]),
                    "concluido": bool(r[15]),
                    "total_inscritos": int(r[16] or 0),
                }
                for r in rows
            ]
            return {"total": total, "items": items}
        finally:
            cur.close()

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
                       IF(A.ideia_inicial           IS NULL, 0, 1) AS has_ideia_inicial,
                       IF(A.ideia_inicial_pdf       IS NULL, 0, 1) AS has_ideia_inicial_pdf,
                       IF(A.mon_parcial_docx_file   IS NULL, 0, 1) AS has_mon_parcial_docx,
                       IF(A.mon_parcial_pdf_file    IS NULL, 0, 1) AS has_mon_parcial_pdf,
                       IF(A.mon_final_docx_file     IS NULL, 0, 1) AS has_mon_final_docx,
                       IF(A.mon_final_pdf_file      IS NULL, 0, 1) AS has_mon_final_pdf
                  FROM tb_novo_projeto AS A
             LEFT JOIN tb_cadastro_orientador AS B ON A.id_orientador = B.id_orientador
             LEFT JOIN tb_campus               AS C ON A.id_campus     = C.id_campus
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
                    "has_ideia_inicial": bool(r[6]),
                    "has_ideia_inicial_pdf": bool(r[7]),
                    "has_mon_parcial_docx": bool(r[8]),
                    "has_mon_parcial_pdf": bool(r[9]),
                    "has_mon_final_docx": bool(r[10]),
                    "has_mon_final_pdf": bool(r[11]),
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

    # ---- novos helpers para 'ideia_inicial' (DOCX) e 'ideia_inicial_pdf' ----
    # (corrige o typo "incicial" e mantém métodos claros)
    def update_ideia_inicial_file(self, id_projeto: int, data: bytes) -> None:
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

    def get_ideia_inicial_file(self, id_projeto: int) -> bytes | None:
        c = self.db_conn.cursor()
        try:
            c.execute("SELECT ideia_inicial FROM tb_novo_projeto WHERE id_projeto=%s", (id_projeto,))
            row = c.fetchone()
            return row[0] if row and row[0] is not None else None
        finally:
            c.close()

    def update_ideia_inicial_pdf_file(self, id_projeto: int, data: bytes) -> None:
        if not data:
            raise ValueError("Arquivo PDF inválido.")
        c = self.db_conn.cursor()
        try:
            c.execute("UPDATE tb_novo_projeto SET ideia_inicial_pdf=%s WHERE id_projeto=%s", (data, id_projeto))
            self.db_conn.commit()
            if c.rowcount == 0:
                raise ValueError("Projeto não encontrado.")
        finally:
            c.close()

    def get_ideia_inicial_pdf_file(self, id_projeto: int) -> bytes | None:
        c = self.db_conn.cursor()
        try:
            c.execute("SELECT ideia_inicial_pdf FROM tb_novo_projeto WHERE id_projeto=%s", (id_projeto,))
            row = c.fetchone()
            return row[0] if row and row[0] is not None else None
        finally:
            c.close()

    # meta para envio por e-mail (prioriza final PDF > parcial PDF > ideia_inicial_pdf)
    def get_meta_e_pdf(self, id_projeto: int):
        cur = self.db_conn.cursor()
        try:
            cur.execute(
                """
                SELECT titulo_projeto,
                       COALESCE(mon_final_pdf_file, mon_parcial_pdf_file, ideia_inicial_pdf) AS pdf_file
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
                SELECT id_projeto,
                       cod_projeto,
                       titulo_projeto,
                       resumo,
                       id_orientador,
                       id_campus,
                       IF(ideia_inicial           IS NULL, 0, 1) AS has_ideia_inicial,
                       IF(ideia_inicial_pdf       IS NULL, 0, 1) AS has_ideia_inicial_pdf,
                       IF(mon_parcial_docx_file   IS NULL, 0, 1) AS has_mon_parcial_docx,
                       IF(mon_parcial_pdf_file    IS NULL, 0, 1) AS has_mon_parcial_pdf,
                       IF(mon_final_docx_file     IS NULL, 0, 1) AS has_mon_final_docx,
                       IF(mon_final_pdf_file      IS NULL, 0, 1) AS has_mon_final_pdf
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
                "has_ideia_inicial": bool(r[6]),
                "has_ideia_inicial_pdf": bool(r[7]),
                "has_mon_parcial_docx": bool(r[8]),
                "has_mon_parcial_pdf": bool(r[9]),
                "has_mon_final_docx": bool(r[10]),
                "has_mon_final_pdf": bool(r[11]),
            }
        finally:
            c.close()

    # (mantidos, sem mudanças)
    def salvar_envio_avaliadores(self, id_projeto: int, destinatarios: list) -> None:
        cursor = self.db_conn.cursor()
        try:
            fmt = ",".join(["%s"] * len(destinatarios))
            cursor.execute(
                f"SELECT id_avaliador, email FROM TB_AVALIADOR_EXTERNO WHERE email IN ({fmt})",
                destinatarios,
            )
            avaliadores = cursor.fetchall()
            if not avaliadores:
                raise ValueError("Nenhum avaliador encontrado com os e-mails fornecidos.")

            values = [(id_projeto, row[0]) for row in avaliadores]
            cursor.executemany(
                "INSERT INTO tb_envio_avaliadores (id_projeto, id_avaliador) VALUES (%s, %s)",
                values,
            )
            self.db_conn.commit()
        finally:
            cursor.close()

    def get_all_envios(self) -> list:
        cursor = self.db_conn.cursor()
        try:
            cursor.execute(
                """
                SELECT ea.id_envio, ea.data_envio, a.nome, p.titulo_projeto
                  FROM tb_envio_avaliadores ea
                  JOIN TB_AVALIADOR_EXTERNO a ON ea.id_avaliador = a.id_avaliador
                  JOIN tb_novo_projeto p       ON ea.id_projeto   = p.id_projeto
                """
            )
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
        finally:
            cursor.close()

    def get_envio_by_id(self, id_envio: int) -> Optional[dict]:
        cursor = self.db_conn.cursor()
        try:
            cursor.execute(
                """
                SELECT ea.id_envio, ea.data_envio, a.nome, p.titulo_projeto
                  FROM tb_envio_avaliadores ea
                  JOIN TB_AVALIADOR_EXTERNO a ON ea.id_avaliador = a.id_avaliador
                  JOIN tb_novo_projeto p       ON ea.id_projeto   = p.id_projeto
                 WHERE ea.id_envio = %s
                """,
                (id_envio,),
            )
            row = cursor.fetchone()
            if row:
                return {
                    "id_envio": row[0],
                    "data_envio": row[1],
                    "avaliador_nome": row[2],
                    "titulo_projeto": row[3],
                }
            return None
        finally:
            cursor.close()

    # --- MONOGRAFIA PARCIAL ---
    def update_mon_parcial_docx(self, id_projeto: int, data: bytes) -> None:
        if not data:
            raise ValueError("Arquivo DOCX inválido.")
        c = self.db_conn.cursor()
        try:
            c.execute(
                "UPDATE tb_novo_projeto SET mon_parcial_docx_file=%s WHERE id_projeto=%s",
                (data, id_projeto),
            )
            self.db_conn.commit()
            if c.rowcount == 0:
                raise ValueError("Projeto não encontrado.")
        finally:
            c.close()

    def update_mon_parcial_pdf(self, id_projeto: int, data: bytes) -> None:
        if not data:
            raise ValueError("Arquivo PDF inválido.")
        c = self.db_conn.cursor()
        try:
            c.execute(
                "UPDATE tb_novo_projeto SET mon_parcial_pdf_file=%s WHERE id_projeto=%s",
                (data, id_projeto),
            )
            self.db_conn.commit()
            if c.rowcount == 0:
                raise ValueError("Projeto não encontrado.")
        finally:
            c.close()

    # --- MONOGRAFIA FINAL ---
    def update_mon_final_docx(self, id_projeto: int, data: bytes) -> None:
        if not data:
            raise ValueError("Arquivo DOCX inválido.")
        c = self.db_conn.cursor()
        try:
            c.execute(
                "UPDATE tb_novo_projeto SET mon_final_docx_file=%s WHERE id_projeto=%s",
                (data, id_projeto),
            )
            self.db_conn.commit()
            if c.rowcount == 0:
                raise ValueError("Projeto não encontrado.")
        finally:
            c.close()

    def update_mon_final_pdf(self, id_projeto: int, data: bytes) -> None:
        if not data:
            raise ValueError("Arquivo PDF inválido.")
        c = self.db_conn.cursor()
        try:
            c.execute(
                "UPDATE tb_novo_projeto SET mon_final_pdf_file=%s WHERE id_projeto=%s",
                (data, id_projeto),
            )
            self.db_conn.commit()
            if c.rowcount == 0:
                raise ValueError("Projeto não encontrado.")
        finally:
            c.close()

    def get_mon_parcial_docx_file(self, id_projeto: int) -> bytes | None:
        c = self.db_conn.cursor()
        try:
            c.execute("SELECT mon_parcial_docx_file FROM tb_novo_projeto WHERE id_projeto=%s", (id_projeto,))
            row = c.fetchone()
            return row[0] if row and row[0] is not None else None
        finally:
            c.close()

    def get_mon_parcial_pdf_file(self, id_projeto: int) -> bytes | None:
        c = self.db_conn.cursor()
        try:
            c.execute("SELECT mon_parcial_pdf_file FROM tb_novo_projeto WHERE id_projeto=%s", (id_projeto,))
            row = c.fetchone()
            return row[0] if row and row[0] is not None else None
        finally:
            c.close()

    def get_mon_final_docx_file(self, id_projeto: int) -> bytes | None:
        c = self.db_conn.cursor()
        try:
            c.execute("SELECT mon_final_docx_file FROM tb_novo_projeto WHERE id_projeto=%s", (id_projeto,))
            row = c.fetchone()
            return row[0] if row and row[0] is not None else None
        finally:
            c.close()

    def get_mon_final_pdf_file(self, id_projeto: int) -> bytes | None:
        c = self.db_conn.cursor()
        try:
            c.execute("SELECT mon_final_pdf_file FROM tb_novo_projeto WHERE id_projeto=%s", (id_projeto,))
            row = c.fetchone()
            return row[0] if row and row[0] is not None else None
        finally:
            c.close()

    def list_aluno_ids_by_projeto(self, id_projeto: int) -> List[int]:
        cur = self.db_conn.cursor()
        try:
            cur.execute(
                """
                SELECT pa.id_aluno
                  FROM tb_projeto_aluno pa
                 WHERE pa.id_projeto = %s
                """,
                (id_projeto,)
            )
            rows = cur.fetchall()
            return [r[0] for r in rows]
        finally:
            cur.close()

    def concluir(self, id_projeto: int) -> None:
        cursor = self.db_conn.cursor()
        try:
            cursor.execute(
                "UPDATE tb_novo_projeto SET concluido = TRUE WHERE id_projeto = %s", (id_projeto,)
            )
            self.db_conn.commit()
            if cursor.rowcount == 0:
                raise ValueError("Projeto não encontrado ou já está concluído.")
        finally:
            cursor.close()

    def get_orientador_id_by_projeto(self, id_projeto: int) -> Optional[int]:
        cur = self.db_conn.cursor()
        try:
            cur.execute(
                "SELECT id_orientador FROM tb_novo_projeto WHERE id_projeto = %s LIMIT 1",
                (id_projeto,)
            )
            row = cur.fetchone()
            if not row:
                return None
            return row[0]
        finally:
            cur.close()