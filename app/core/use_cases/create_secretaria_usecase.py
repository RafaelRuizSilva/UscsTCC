from app.core.models.secretaria import Secretaria
from app.core.ports.output.porta_secretaria_repository import ISecretariaRepository

class CreateSecretariaUseCase:
    def __init__(self, repo: ISecretariaRepository) -> None:
        self._repo = repo

    def execute(self, secretaria: Secretaria) -> int:
        return self._repo.create(secretaria)
