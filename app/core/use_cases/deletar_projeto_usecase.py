from app.core.ports.output.porta_projeto_repository import IProjetoRepository

class DeletarProjetoUseCase:
    def __init__(self, repo: IProjetoRepository):
        self.repo = repo

    def execute(self, id_projeto: int):
        self.repo.deletar_por_id(id_projeto)
