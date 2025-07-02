from app.core.models.projeto import Projeto
from app.core.ports.output.porta_projeto_repository import IProjetoRepository

class CreateProjetoUseCase:
    def __init__(self, repo: IProjetoRepository):
        self.repo = repo

    def execute(self, projeto: Projeto) -> int:
        return self.repo.create(projeto)