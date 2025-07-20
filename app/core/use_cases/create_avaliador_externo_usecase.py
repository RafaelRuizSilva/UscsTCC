from app.core.models.avaliador_externo import AvaliadorExternoCreate
from app.core.ports.output.porta_avaliador_externo_repository import IAvaliadorExternoRepository

class CreateAvaliadorExternoUseCase:
    def __init__(self, repo: IAvaliadorExternoRepository):
        self.repo = repo

    def execute(self, avaliador: AvaliadorExternoCreate) -> int:
        return self.repo.create(avaliador)
