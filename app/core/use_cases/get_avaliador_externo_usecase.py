from app.core.ports.output.porta_avaliador_externo_repository import IAvaliadorExternoRepository

class GetAvaliadorExternoUseCase:
    def __init__(self, repo: IAvaliadorExternoRepository) -> None:
        self._repo = repo

    def execute(self, id_avaliador: int) -> dict | None:
        return self._repo.get_by_id(id_avaliador)
