from typing import List, Dict
from app.core.ports.output.porta_bolsa_repository import IBolsaRepository
from pymysql.err import IntegrityError

class BolsaRepository(IBolsaRepository):
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def list_all(self) -> List[Dict]:
        """
        Lista todas as bolsas com dados básicos do aluno.
        """
        cur = self.db_conn.cursor()
        try:
            query = """
                SELECT a.id_aluno,
                       a.nome_completo,
                       a.email,
                       IFNULL(b.possui_bolsa, 0) AS possui_bolsa
                  FROM tb_cadastro_aluno a
             LEFT JOIN tb_bolsa_aluno   b ON b.id_aluno = a.id_aluno
              ORDER BY a.nome_completo ASC
            """
            cur.execute(query)
            rows = cur.fetchall()
            return [
                {
                    "id_aluno": r[0],
                    "nome_completo": r[1],
                    "email": r[2],
                    "possui_bolsa": bool(r[3]),
                }
                for r in rows
            ]
        finally:
            cur.close()

    def set_possui_bolsa(self, id_aluno: int, possui_bolsa: bool) -> None:
        """
        Upsert: cria o registro se não existir, atualiza se já existir.
        Requer UNIQUE (id_aluno) em tb_bolsa_aluno.
        """
        cur = self.db_conn.cursor()
        try:
            sql = """
                INSERT INTO tb_bolsa_aluno (id_aluno, possui_bolsa)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE possui_bolsa = VALUES(possui_bolsa)
            """
            cur.execute(sql, (id_aluno, 1 if possui_bolsa else 0))
            self.db_conn.commit()
        except IntegrityError as e:
            # se o aluno não existir (FK), cai aqui
            msg = str(e).lower()
            if "foreign key constraint fails" in msg:
                raise ValueError("Aluno inválido (id_aluno não existe).")
            else:
                raise
        finally:
            cur.close()

    def create(self, id_aluno: int, possui_bolsa: bool) -> int:
        cur = self.db_conn.cursor()
        try:
            cur.execute(
                "INSERT INTO tb_bolsa_aluno (id_aluno, possui_bolsa) VALUES (%s, %s)",
                (id_aluno, 1 if possui_bolsa else 0),
            )
            self.db_conn.commit()
            return cur.lastrowid
        except IntegrityError as e:
            msg = str(e).lower()
            if "duplicate entry" in msg:
                raise ValueError("Este aluno já possui registro de bolsa.")
            if "foreign key constraint fails" in msg:
                raise ValueError("Aluno inválido (id_aluno não existe).")
            raise
        finally:
            cur.close()