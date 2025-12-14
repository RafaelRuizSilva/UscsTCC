from typing import List
from app.core.ports.output.porta_upd_aluno_projeto import IProjetoGateway

class ProjetoGateway(IProjetoGateway):
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def atualizar_alunos_projeto(self, id_projeto: int, id_alunos: List[int]):
        """
        Registra a seleção FINAL de alunos de um projeto.

        Regras:
        - tb_inscricao_projeto guarda inscrições (candidatos).
        - tb_projeto_aluno guarda apenas vínculos definitivos.
        - Um aluno só pode estar definitivo em UM projeto por vez.
        - Quando o aluno vira definitivo em um projeto, as inscrições
          dele nos OUTROS projetos são apagadas.
        """

        cursor = self.db_conn.cursor()
        try:
            # 0) Garante que o projeto existe
            cursor.execute(
                "SELECT 1 FROM tb_novo_projeto WHERE id_projeto = %s LIMIT 1",
                (id_projeto,),
            )
            if cursor.fetchone() is None:
                raise ValueError("Projeto não encontrado.")

            # 1) Remove vínculos definitivos atuais deste projeto
            cursor.execute(
                "DELETE FROM tb_projeto_aluno WHERE id_projeto = %s",
                (id_projeto,),
            )

            # 2) Para cada aluno aprovado:
            for id_aluno in id_alunos:
                # 2.1) Remove vínculos definitivos dele em OUTROS projetos
                cursor.execute(
                    """
                    DELETE FROM tb_projeto_aluno
                     WHERE id_aluno   = %s
                       AND id_projeto <> %s
                    """,
                    (id_aluno, id_projeto),
                )

                # 2.2) Remove INSCRIÇÕES dele em OUTROS projetos
                cursor.execute(
                    """
                    DELETE FROM tb_inscricao_projeto
                     WHERE id_aluno   = %s
                       AND id_projeto <> %s
                    """,
                    (id_aluno, id_projeto),
                )

                # 2.3) Cria vínculo definitivo neste projeto
                cursor.execute(
                    """
                    INSERT INTO tb_projeto_aluno (id_aluno, id_projeto, status_aluno)
                    VALUES (%s, %s, TRUE)
                    """,
                    (id_aluno, id_projeto),
                )

            self.db_conn.commit()

        finally:
            cursor.close()
