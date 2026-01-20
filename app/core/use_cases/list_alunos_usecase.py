from app.core.ports.output.porta_aluno_repository import IAlunoRepository

class ListAlunosUseCase:
    def __init__(self, repo: IAlunoRepository) -> None:
        self._repo = repo

    def execute(self) -> list[dict]:
        return self._repo.list_all()
