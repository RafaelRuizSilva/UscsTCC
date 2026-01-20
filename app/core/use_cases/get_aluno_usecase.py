# app/core/usecases/aluno/get_aluno_by_id.py
from app.core.ports.output.porta_aluno_repository import IAlunoRepository

class GetAlunoByIdUseCase:
    def __init__(self, repo: IAlunoRepository) -> None:
        self._repo = repo

    def execute(self, aluno_id: int) -> dict | None:
        return self._repo.get_by_id(aluno_id)
