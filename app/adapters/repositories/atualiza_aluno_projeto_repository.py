from typing import List
from pymysql.connections import Connection

class ProjetoGateway:
    def __init__(self, db_conn: Connection):
        self.db_conn = db_conn

    def atualizar_alunos_projeto(self, id_projeto: int, id_alunos: List[int]):
        cur = self.db_conn.cursor()
        try:
            # projeto existe?
            cur.execute("SELECT 1 FROM tb_novo_projeto WHERE id_projeto=%s", (id_projeto,))
            if not cur.fetchone():
                raise ValueError("Projeto não encontrado")

            # limpa vínculos
            cur.execute("DELETE FROM tb_projeto_aluno WHERE id_projeto=%s", (id_projeto,))

            # insere novos (se houver)
            if id_alunos:
                cur.executemany(
                    "INSERT INTO tb_projeto_aluno (id_projeto, id_aluno) VALUES (%s, %s)",
                    [(id_projeto, aid) for aid in id_alunos],
                )
            self.db_conn.commit()
        except Exception:
            self.db_conn.rollback()
            raise
        finally:
            cur.close()
