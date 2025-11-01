from app.core.ports.output.porta_curso_repository import ICursoRepository
from app.core.models.curso import Curso

class UpdateCursoUseCase:
    def __init__(self, repo: ICursoRepository):
        self.repo = repo

    def execute(self, curso_id: int, curso: Curso) -> None:
        self.repo.update(curso_id, curso)