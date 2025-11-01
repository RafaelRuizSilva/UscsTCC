from app.core.ports.output.porta_curso_repository import ICursoRepository


class GetCursoByIdUseCase:
    def __init__(self, repo: ICursoRepository):
        self.repo = repo

    def execute(self, curso_id: int) -> dict:
        return self.repo.get_by_id(curso_id)