from app.core.ports.output.porta_relatorio_repository import IRelatorioRepository

class RelatorioRepository(IRelatorioRepository):
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def listar_alunos_nome_cpf(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT nome_completo, cpf FROM tb_cadastro_aluno")
        return cursor.fetchall()
