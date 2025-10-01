from app.core.models.aluno import Aluno
from app.core.ports.output.porta_aluno_repository import IAlunoRepository

class CreateAlunoUseCase:
    def __init__(self, repo: IAlunoRepository) -> None:
        self._repo = repo

    def execute(self, aluno: Aluno, pdf_bytes: bytes) -> int:
        return self._repo.create(aluno, pdf_bytes)
