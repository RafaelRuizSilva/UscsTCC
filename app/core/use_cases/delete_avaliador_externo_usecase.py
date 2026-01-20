from app.core.ports.output.porta_avaliador_externo_repository import IAvaliadorExternoRepository

class DeleteAvaliadorExternoUseCase:
    def __init__(self, repo: IAvaliadorExternoRepository) -> None:
        self._repo = repo

    def execute(self, id_avaliador: int) -> None:
        self._repo.delete(id_avaliador)
