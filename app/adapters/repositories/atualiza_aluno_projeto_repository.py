from typing import List
from app.core.ports.output.porta_upd_aluno_projeto import IProjetoGateway
from pymysql.connections import Connection

class ProjetoGateway(IProjetoGateway):
    def __init__(self, db_conn: Connection):
        self.db_conn = db_conn

    def atualizar_alunos_projeto(self, id_projeto: int, id_alunos: List[int]):
        cursor = self.db_conn.cursor()

        # Verifica se projeto existe
        cursor.execute("SELECT 1 FROM tb_novo_projeto WHERE id_projeto = %s", (id_projeto,))
        if not cursor.fetchone():
            raise ValueError("Projeto não encontrado")

        # Limpa vínculos existentes
        cursor.execute("DELETE FROM tb_projeto_aluno WHERE id_projeto = %s", (id_projeto,))

        # Insere novos vínculos
        for id_aluno in id_alunos:
            cursor.execute(
                "INSERT INTO tb_projeto_aluno (id_projeto, id_aluno) VALUES (%s, %s)",
                (id_projeto, id_aluno)
            )

        self.db_conn.commit()
