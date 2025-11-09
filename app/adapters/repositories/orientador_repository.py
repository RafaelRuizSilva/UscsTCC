from typing import List, Optional
from pymysql.err import IntegrityError
from datetime import date, timedelta

from app.core.models.orientador import Orientador
from app.core.models.orientador_out import OrientadorOut
from app.core.ports.output.porta_orientador_repository import IOrientadorRepository

class OrientadorRepository(IOrientadorRepository):
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create(self, orientador: Orientador) -> int:
        cur = self.db_conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO tb_cadastro_orientador (nome_completo, email, cpf, senha_hash)
                VALUES (%s, %s, %s, %s)
                """,
                (orientador.nome_completo.lower(), orientador.email, orientador.cpf, orientador.senha_hash)
            )
            self.db_conn.commit()
            return cur.lastrowid
        except IntegrityError as err:
            msg = str(err).lower()
            if "duplicate entry" in msg and "cpf" in msg:
                raise ValueError("CPF já cadastrado.")
            elif "duplicate entry" in msg and "email" in msg:
                raise ValueError("E-mail já cadastrado.")
            else:
                raise
        finally:
            cur.close()

    def listar_todos(self) -> List[OrientadorOut]:
        cur = self.db_conn.cursor()
        try:
            cur.execute(
                """
                SELECT id_orientador, nome_completo, email, cpf, COALESCE(status,'') AS status
                  FROM tb_cadastro_orientador
              ORDER BY id_orientador DESC
                """
            )
            return [self._row_to_out(r) for r in cur.fetchall()]
        finally:
            cur.close()

    def obter_por_id(self, orientador_id: int) -> Optional[OrientadorOut]:
        cur = self.db_conn.cursor()
        try:
            cur.execute(
                """
                SELECT id_orientador, nome_completo, email, cpf, COALESCE(status,'') AS status
                  FROM tb_cadastro_orientador
                 WHERE id_orientador = %s
                 LIMIT 1
                """,
                (orientador_id,)
            )
            r = cur.fetchone()
            return self._row_to_out(r) if r else None
        finally:
            cur.close()

    def obter_por_nome(self, nome: str) -> Optional[OrientadorOut]:
        cur = self.db_conn.cursor()
        try:
            like_term = f"%{nome.strip().lower()}%"
            cur.execute(
                """
                SELECT id_orientador, nome_completo, email, cpf, COALESCE(status,'') AS status
                  FROM tb_cadastro_orientador
                 WHERE LOWER(nome_completo) LIKE %s
              ORDER BY id_orientador DESC
                 LIMIT 1
                """,
                (like_term,)
            )
            r = cur.fetchone()
            return self._row_to_out(r) if r else None
        finally:
            cur.close()

    def _row_to_out(self, row) -> OrientadorOut:
        return OrientadorOut(
            id=row[0],
            nome_completo=row[1],
            email=row[2],
            cpf=row[3],
            status=row[4],
        )

    def update_status(self, orientador_id: int, novo_status: str) -> None:
        cur = self.db_conn.cursor()
        try:
            if str(novo_status).upper() == "REPROVADO" or str(novo_status).upper() == "INADIMPLENTE" :
                inad_until = date.today() + timedelta(days=365*2)  # DATE, igual ao aluno
                cur.execute(
                    "UPDATE tb_cadastro_orientador SET status=%s, inadimplente_ate=%s WHERE id_orientador=%s",
                    (novo_status, inad_until, orientador_id)
                )
            else:
                cur.execute(
                    "UPDATE tb_cadastro_orientador SET status=%s, inadimplente_ate=NULL WHERE id_orientador=%s",
                    (novo_status, orientador_id)
                )

            self.db_conn.commit()
            if cur.rowcount == 0:
                raise ValueError("Orientador não encontrado.")
        finally:
            cur.close()

    def list_inadimplentes(self) -> list[dict]:
        cur = self.db_conn.cursor()
        try:
            cur.execute(
                """
                SELECT id_orientador, nome_completo, email, cpf, status, inadimplente_ate
                  FROM tb_cadastro_orientador
                WHERE status = 'INADIMPLENTE'

                """
            )
            return [
                {
                    "id": r[0], "nome_completo": r[1], "email": r[2], "cpf": r[3],
                    "status": r[4],
                    "inadimplente_ate": r[5].isoformat() if r[5] else None
                }
                for r in cur.fetchall()
            ]
        finally:
            cur.close()

    def get_status_flags(self, orientador_id: int) -> dict | None:
        cur = self.db_conn.cursor()
        try:
            cur.execute(
                "SELECT status, inadimplente_ate FROM tb_cadastro_orientador WHERE id_orientador=%s",
                (orientador_id,)
            )
            r = cur.fetchone()
            if not r: return None
            return {"status": r[0], "inadimplente_ate": r[1]}
        finally:
            cur.close()

    def listar_aprovados(self) -> list[OrientadorOut]:
        cur = self.db_conn.cursor()
        try:
            cur.execute(
                """
                SELECT id_orientador, nome_completo, email, cpf, 'APROVADO' AS status
                  FROM tb_cadastro_orientador
                 WHERE status='APROVADO'
                   AND (inadimplente_ate IS NULL OR inadimplente_ate <= NOW())
              ORDER BY nome_completo ASC
                """
            )
            return [self._row_to_out(r) for r in cur.fetchall()]
        finally:
            cur.close()
