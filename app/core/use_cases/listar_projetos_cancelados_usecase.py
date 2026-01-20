from app.core.ports.output.porta_projeto_repository import IProjetoRepository


class ListarProjetosCanceladosUseCase:
    def __init__(self, repo: IProjetoRepository):
        self.repo = repo

    def execute(self):
        return self.repo.listar_projetos_cancelados()
