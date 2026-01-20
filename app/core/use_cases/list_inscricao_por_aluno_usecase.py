from app.core.ports.output.porta_inscricao_repository import IInscricaoRepository

class ListarInscricoesPorAlunoUseCase:
    def __init__(self, repo: IInscricaoRepository):
        self.repo = repo

    def execute(self, id_aluno: int) -> list[dict]:
        return self.repo.list_by_aluno(id_aluno)
