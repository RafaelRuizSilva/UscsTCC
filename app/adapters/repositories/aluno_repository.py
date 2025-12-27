from app.core.models.aluno import Aluno
from pymysql.err import IntegrityError
from datetime import date, timedelta
from typing import Sequence

class AlunoRepository:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create(self, aluno: Aluno, pdf_bytes: bytes) -> int:
        cursor = self.db_conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO tb_cadastro_aluno
                    (nome_completo, email, cpf, id_curso, possui_trabalho_remunerado, senha_hash, status, pdf_file)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
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
        cur = self.db_conn.cursor()
        try:
            cur.execute(
                """
                SELECT id_aluno, nome_completo, email, cpf, id_curso,
                       possui_trabalho_remunerado, status,
                       IF(pdf_file IS NULL, 0, 1) AS has_pdf
                  FROM tb_cadastro_aluno
              ORDER BY nome_completo ASC
                """
            )
            rows = cur.fetchall()
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
            cur.close()

    def get_by_id(self, aluno_id: int) -> dict | None:
        cur = self.db_conn.cursor()
        try:
            cur.execute(
                """
                SELECT id_aluno, nome_completo, email, cpf, id_curso,
                       possui_trabalho_remunerado, status,
                       IF(pdf_file IS NULL, 0, 1) AS has_pdf
                  FROM tb_cadastro_aluno
                 WHERE id_aluno = %s
                """,
                (aluno_id,)
            )
            r = cur.fetchone()
            if not r:
                return None
            return {
                "id": r[0],
                "nome_completo": r[1],
                "email": r[2],
                "cpf": r[3],
                "id_curso": r[4],
                "possui_trabalho_remunerado": r[5],
                "status": r[6],
                "has_pdf": bool(r[7]),
            }
        finally:
            cur.close()

    def delete(self, aluno_id: int) -> None:
        cur = self.db_conn.cursor()
        try:
            cur.execute("DELETE FROM tb_cadastro_aluno WHERE id_aluno = %s", (aluno_id,))
            self.db_conn.commit()
            if cur.rowcount == 0:
                raise ValueError("Aluno não encontrado.")
        finally:
            cur.close()

    def update_status(self, aluno_id: int, novo_status: str) -> None:
        cur = self.db_conn.cursor()
        try:
            novo_status = str(novo_status).upper()

            if novo_status == "INADIMPLENTE":
                inad_until = date.today() + timedelta(days=365 * 2)

                cur.execute(
                    """
                    UPDATE tb_cadastro_aluno
                    SET status=%s,
                        inadimplente_ate=%s
                    WHERE id_aluno = %s
                    """,
                    (novo_status, inad_until, aluno_id),
                )

                # 🔥 REGRA NOVA — PERDE A BOLSA
                cur.execute(
                    "DELETE FROM tb_bolsa WHERE id_aluno = %s",
                    (aluno_id,),
                )

            elif novo_status == "REPROVADO":
                inad_until = date.today() + timedelta(days=365 * 2)

                cur.execute(
                    """
                    UPDATE tb_cadastro_aluno
                    SET status=%s,
                        inadimplente_ate=%s
                    WHERE id_aluno = %s
                    """,
                    (novo_status, inad_until, aluno_id),
                )

                # ❌ Reprovado também perde bolsa
                cur.execute(
                    "DELETE FROM tb_bolsa WHERE id_aluno = %s",
                    (aluno_id,),
                )

            else:
                # APROVADO / PENDENTE
                cur.execute(
                    """
                    UPDATE tb_cadastro_aluno
                    SET status=%s,
                        inadimplente_ate=NULL
                    WHERE id_aluno = %s
                    """,
                    (novo_status, aluno_id),
                )

            self.db_conn.commit()

        finally:
            cur.close()

    def get_status(self, id_aluno: int) -> str:
        cursor = self.db_conn.cursor()
        try:
            cursor.execute(
                "SELECT status FROM tb_cadastro_aluno WHERE id_aluno = %s",
                (id_aluno,),
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError("Aluno não encontrado.")
            return row[0]
        finally:
            cursor.close()

    def get_pdf_by_id(self, aluno_id: int) -> bytes | None:
        cur = self.db_conn.cursor()
        try:
            cur.execute("SELECT pdf_file FROM tb_cadastro_aluno WHERE id_aluno=%s", (aluno_id,))
            r = cur.fetchone()
            return r[0] if r and r[0] is not None else None
        finally:
            cur.close()

    def list_inadimplentes(self) -> list[dict]:
        cur = self.db_conn.cursor()
        try:
            cur.execute(
                """
                SELECT id_aluno, nome_completo, email, cpf, status, inadimplente_ate
                  FROM tb_cadastro_aluno
                 WHERE status = 'INADIMPLENTE'
                """
            )
            rows = cur.fetchall()
            return [
                {
                    "id": r[0], "nome_completo": r[1], "email": r[2], "cpf": r[3],
                    "status": r[4],
                    "inadimplente_ate": r[5].isoformat() if r[5] else None
                }
                for r in rows
            ]
        finally:
            cur.close()

    def get_status_flags(self, aluno_id: int) -> dict | None:
        cur = self.db_conn.cursor()
        try:
            cur.execute(
                "SELECT status, inadimplente_ate FROM tb_cadastro_aluno WHERE id_aluno=%s",
                (aluno_id,)
            )
            r = cur.fetchone()
            if not r:
                return None
            return {"status": r[0], "inadimplente_ate": r[1]}
        finally:
            cur.close()

    def update_status_many_reprovado(self, aluno_ids: Sequence[int]) -> int:
        if not aluno_ids:
            return 0

        cur = self.db_conn.cursor()
        try:
            inad_until = date.today() + timedelta(days=365 * 2)
            placeholders = ",".join(["%s"] * len(aluno_ids))

            sql = f"""
                UPDATE tb_cadastro_aluno
                   SET status=%s, inadimplente_ate=%s
                 WHERE id_aluno IN ({placeholders})
            """
            params = ["INADIMPLENTE", inad_until, *aluno_ids]
            cur.execute(sql, params)

            # 🔥 REMOVE BOLSAS DE TODOS
            cur.execute(
                f"DELETE FROM tb_bolsa WHERE id_aluno IN ({placeholders})",
                aluno_ids,
            )

            self.db_conn.commit()
            return cur.rowcount or 0

        finally:
            cur.close()
