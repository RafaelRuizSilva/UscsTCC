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
