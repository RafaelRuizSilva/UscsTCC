# app/adapters/repositories/bolsa_repository.py
from typing import List, Dict, Optional
from app.core.ports.output.porta_bolsa_repository import IBolsaRepository
from app.core.models.bolsa import BolsaCreate
from pymysql.err import IntegrityError

class BolsaRepository(IBolsaRepository):
    def __init__(self, db_conn):
        self.db = db_conn

    def create(self, data: BolsaCreate) -> int:
        cur = self.db.cursor()
        try:
            # garante que tipo existe
            cur.execute("SELECT 1 FROM tb_tipo_bolsa WHERE id_tipo_bolsa=%s", (data.id_tipo_bolsa,))
            if not cur.fetchone():
                raise ValueError("Tipo de bolsa inexistente.")

            # garante que aluno existe
            cur.execute("SELECT 1 FROM tb_cadastro_aluno WHERE id_aluno=%s", (data.id_aluno,))
            if not cur.fetchone():
                raise ValueError("Aluno inexistente.")

            cur.execute(
                """
                INSERT INTO tb_bolsa (id_aluno, id_tipo_bolsa)
                VALUES (%s, %s)
                """,
                (data.id_aluno, data.id_tipo_bolsa)
            )
            self.db.commit()
            new_id = cur.lastrowid

            # seta flag do aluno
            self.set_aluno_possui_bolsa(data.id_aluno, True)
            return new_id
        except IntegrityError as e:
            # pode ser UNIQUE uq_aluno_tipo
            raise ValueError("Este aluno já possui essa bolsa.") from e
        finally:
            cur.close()

    def delete_by_id(self, id_bolsa: int) -> int:
        cur = self.db.cursor()
        try:
            # pega dono
            cur.execute("SELECT id_aluno FROM tb_bolsa WHERE id_bolsa=%s", (id_bolsa,))
            row = cur.fetchone()
            if not row:
                return 0
            id_aluno = row[0]

            cur.execute("DELETE FROM tb_bolsa WHERE id_bolsa=%s", (id_bolsa,))
            self.db.commit()
            affected = cur.rowcount

            # se não sobrou nenhuma bolsa, limpa a flag
            if affected and not self.exists_any_for_aluno(id_aluno):
                self.set_aluno_possui_bolsa(id_aluno, False)

            return affected
        finally:
            cur.close()

    def list_all(self, limit: int, offset: int) -> List[Dict]:
        cur = self.db.cursor()
        try:
            cur.execute(
                """
                SELECT b.id_bolsa,
                       b.id_aluno,
                       a.nome_completo,
                       a.email,
                       b.id_tipo_bolsa,
                       t.tipo_bolsa,
                       b.created_at
                  FROM tb_bolsa b
                  JOIN tb_cadastro_aluno a ON a.id_aluno = b.id_aluno
                  JOIN tb_tipo_bolsa t     ON t.id_tipo_bolsa = b.id_tipo_bolsa
              ORDER BY b.created_at DESC
                 LIMIT %s OFFSET %s
                """,
                (limit, offset)
            )
            rows = cur.fetchall()
            return [
                {
                    "id_bolsa": r[0],
                    "id_aluno": r[1],
                    "aluno_nome": r[2],
                    "aluno_email": r[3],
                    "id_tipo_bolsa": r[4],
                    "tipo_bolsa": r[5],
                    "created_at": r[6],
                }
                for r in rows
            ]
        finally:
            cur.close()

    def get_by_id(self, id_bolsa: int) -> Optional[Dict]:
        cur = self.db.cursor()
        try:
            cur.execute(
                """
                SELECT b.id_bolsa,
                       b.id_aluno,
                       a.nome_completo,
                       a.email,
                       b.id_tipo_bolsa,
                       t.tipo_bolsa,
                       b.created_at
                  FROM tb_bolsa b
                  JOIN tb_cadastro_aluno a ON a.id_aluno = b.id_aluno
                  JOIN tb_tipo_bolsa t     ON t.id_tipo_bolsa = b.id_tipo_bolsa
                 WHERE b.id_bolsa = %s
                 LIMIT 1
                """,
                (id_bolsa,)
            )
            r = cur.fetchone()
            if not r:
                return None
            return {
                "id_bolsa": r[0],
                "id_aluno": r[1],
                "aluno_nome": r[2],
                "aluno_email": r[3],
                "id_tipo_bolsa": r[4],
                "tipo_bolsa": r[5],
                "created_at": r[6],
            }
        finally:
            cur.close()

    def exists_any_for_aluno(self, id_aluno: int) -> bool:
        cur = self.db.cursor()
        try:
            cur.execute("SELECT 1 FROM tb_bolsa WHERE id_aluno=%s LIMIT 1", (id_aluno,))
            return cur.fetchone() is not None
        finally:
            cur.close()

    def set_aluno_possui_bolsa(self, id_aluno: int, possui: bool) -> None:
        cur = self.db.cursor()
        try:
            cur.execute(
                "UPDATE tb_cadastro_aluno SET possui_bolsa=%s WHERE id_aluno=%s",
                (1 if possui else 0, id_aluno)
            )
            self.db.commit()
            if cur.rowcount == 0:
                raise ValueError("Aluno não encontrado.")
        finally:
            cur.close()

    def remover_bolsas_por_aluno(self, id_aluno: int) -> int:
        cursor = self.db.cursor()
        try:
            cursor.execute(
                "DELETE FROM tb_bolsa WHERE id_aluno = %s",
                (id_aluno,),
            )
            self.db.commit()
            return cursor.rowcount or 0
        finally:
            cursor.close()