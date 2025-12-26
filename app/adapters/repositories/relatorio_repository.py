from app.core.ports.output.porta_relatorio_repository import IRelatorioRepository

class RelatorioRepository(IRelatorioRepository):
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def listar_alunos_nome_cpf(self):
        cursor = self.db_conn.cursor()

        query = """
                SELECT d.nome_completo as orientador,
                       c.nome_completo as aluno,
                       a.titulo_projeto,
                       a.cod_projeto
                FROM tb_novo_projeto as a
                INNER JOIN tb_projeto_aluno as b
                ON a.id_projeto = b.id_projeto
                
                INNER JOIN tb_cadastro_aluno as c
                ON b.id_aluno = c.id_aluno
                
                INNER JOIN tb_cadastro_orientador as d
                ON a.id_orientador = d.id_orientador
        
        """
        cursor.execute(query)
        return cursor.fetchall()

    def relatorio_workshop(self):
        cursor = self.db_conn.cursor()
        try:
            cursor.execute(
                """
                SELECT nome_completo,
                       email,
                       cpf,
                       NULL AS data_conclusao,
                       NULL AS ciclo
                FROM tb_cadastro_aluno
                WHERE status = 'APROVADO'
                ORDER BY nome_completo
                """
            )

            rows = cursor.fetchall()
            return [
                {
                    "nome": r[0],
                    "email": r[1],
                    "cpf": r[2],
                    "data_conclusao": None,
                    "ciclo": None,
                }
                for r in rows
            ]
        finally:
            cursor.close()

    def relatorio_certificado_final(self):
        cursor = self.db_conn.cursor()
        try:
            cursor.execute(
                """
                SELECT p.cod_projeto,
                       o.nome_completo AS nome_orientador,
                       p.titulo_projeto,
                       a.nome_completo AS nome_aluno
                FROM tb_projeto_aluno pa
                         JOIN tb_novo_projeto p ON p.id_projeto = pa.id_projeto
                         JOIN tb_cadastro_orientador o ON o.id_orientador = p.id_orientador
                         JOIN tb_cadastro_aluno a ON a.id_aluno = pa.id_aluno
                WHERE pa.status_aluno = TRUE
                ORDER BY p.cod_projeto, a.nome_completo
                """
            )

            rows = cursor.fetchall()
            return [
                {
                    "cod_projeto": r[0],
                    "nome_orientador": r[1],
                    "titulo": r[2],
                    "nome_aluno": r[3],
                }
                for r in rows
            ]
        finally:
            cursor.close()