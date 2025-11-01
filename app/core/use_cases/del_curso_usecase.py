from app.core.ports.output.porta_curso_repository import ICursoRepository


class DeleteCursoUseCase:
    def __init__(self, repo: ICursoRepository):
        self.repo = repo

    def execute(self, curso_id: int) -> None:
        self.repo.delete(curso_id)
