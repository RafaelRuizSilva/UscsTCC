from app.core.ports.output.porta_aluno_repository import IAlunoRepository

class ReprovarAlunoUseCase:
    def __init__(self, repo: IAlunoRepository) -> None:
        self._repo = repo

    def execute(self, aluno_id: int) -> None:
        self._repo.update_status(aluno_id, "REPROVADO")
