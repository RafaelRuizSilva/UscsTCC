from app.core.models.orientador import Orientador
from app.core.ports.output.porta_orientador_repository import IOrientadorRepository

class CreateOrientadorUseCase:
    def __init__(self, repo: IOrientadorRepository):
        self.repo = repo

    def execute(self, orientador: Orientador) -> int:
        return self.repo.create(orientador)