from app.core.ports.output.porta_orientador_repository import IOrientadorRepository

class ReprovarOrientadorUseCase:
    def __init__(self, repo: IOrientadorRepository):
        self.repo = repo

    def execute(self, id_orientador: int) -> None:
        self.repo.update_status(id_orientador, "REPROVADO")
