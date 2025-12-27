from app.core.ports.output.porta_secretaria_repository import ISecretariaRepository


class ListarSecretariasUseCase:
    def __init__(self, repo: ISecretariaRepository):
        self.repo = repo

    def execute(self):
        return self.repo.list_all()
