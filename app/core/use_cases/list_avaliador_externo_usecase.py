from app.core.ports.output.porta_avaliador_externo_repository import IAvaliadorExternoRepository

class ListAvaliadorExternoUseCase:
    def __init__(self, repo: IAvaliadorExternoRepository) -> None:
        self._repo = repo

    def execute(self) -> list[dict]:
        return self._repo.list_all()
