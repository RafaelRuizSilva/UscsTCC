import pandas as pd
from app.core.ports.output.porta_relatorio_repository import IRelatorioRepository
import tempfile

class GerarRelatorioAlunosUseCase:
    def __init__(self, repo: IRelatorioRepository):
        self.repo = repo

    def execute(self) -> str:
        alunos = self.repo.listar_alunos_nome_cpf()
        df = pd.DataFrame(alunos, columns=["nome_completo", "cpf"])

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as f:
            df.to_excel(f.name, index=False)
            return f.name
