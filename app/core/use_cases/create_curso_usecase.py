from app.core.models.curso import Curso
from app.core.ports.output.porta_curso_repository import ICursoRepository

class CreateCursoUseCase:
    def __init__(self, repo: ICursoRepository):
        self.repo = repo

    def execute(self, curso: Curso) -> int:
        return self.repo.create(curso)