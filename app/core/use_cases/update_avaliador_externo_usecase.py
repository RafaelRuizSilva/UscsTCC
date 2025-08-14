from app.core.models.avaliador_externo import AvaliadorExternoCreate
from app.core.ports.output.porta_avaliador_externo_repository import IAvaliadorExternoRepository

class UpdateAvaliadorExternoUseCase:
    def __init__(self, repo: IAvaliadorExternoRepository) -> None:
        self._repo = repo

    def execute(self, id_avaliador: int, avaliador: AvaliadorExternoCreate) -> None:
        self._repo.update(id_avaliador, avaliador)
