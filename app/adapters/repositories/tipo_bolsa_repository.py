# app/adapters/repositories/tipo_bolsa_repository.py
from typing import List, Dict, Optional
from app.core.ports.output.porta_tipo_bolsa_repository import ITipoBolsaRepository
from app.core.models.tipo_bolsa import TipoBolsaCreate
from pymysql.err import IntegrityError

class TipoBolsaRepository(ITipoBolsaRepository):
    def __init__(self, db_conn):
        self.db = db_conn

    def create(self, data: TipoBolsaCreate) -> int:
        cur = self.db.cursor()
        try:
            cur.execute(
                "INSERT INTO tb_tipo_bolsa (tipo_bolsa) VALUES (%s)",
                (data.tipo_bolsa,)
            )
            self.db.commit()
            return cur.lastrowid
        except IntegrityError as e:
            # lida com UNIQUE
            raise ValueError("Tipo de bolsa já existe.") from e
        finally:
            cur.close()

    def list_all(self, limit: int, offset: int) -> List[Dict]:
        cur = self.db.cursor()
        try:
            cur.execute(
                "SELECT id_tipo_bolsa, tipo_bolsa FROM tb_tipo_bolsa ORDER BY tipo_bolsa ASC LIMIT %s OFFSET %s",
                (limit, offset)
            )
            rows = cur.fetchall()
            return [{"id_tipo_bolsa": r[0], "tipo_bolsa": r[1]} for r in rows]
        finally:
            cur.close()

    def delete_by_id(self, id_tipo_bolsa: int) -> int:
        cur = self.db.cursor()
        try:
            cur.execute("DELETE FROM tb_tipo_bolsa WHERE id_tipo_bolsa=%s", (id_tipo_bolsa,))
            self.db.commit()
            return cur.rowcount
        finally:
            cur.close()

    def get_by_id(self, id_tipo_bolsa: int) -> Optional[Dict]:
        cur = self.db.cursor()
        try:
            cur.execute(
                "SELECT id_tipo_bolsa, tipo_bolsa FROM tb_tipo_bolsa WHERE id_tipo_bolsa=%s",
                (id_tipo_bolsa,)
            )
            r = cur.fetchone()
            if not r:
                return None
            return {"id_tipo_bolsa": r[0], "tipo_bolsa": r[1]}
        finally:
            cur.close()
