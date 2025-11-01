from app.core.ports.output.porta_inscricao_repository import IInscricaoRepository

class ListarInscricoesPorProjetoUseCase:
    def __init__(self, repo: IInscricaoRepository):
        self.repo = repo

    def execute(self, id_projeto: int) -> list[dict]:
        return self.repo.list_by_projeto(id_projeto)
