from app.core.ports.output.porta_inscricao_repository import IInscricaoRepository

class CriarInscricaoUseCase:
    def __init__(self, repo: IInscricaoRepository):
        self.repo = repo

    def execute(self, id_aluno: int, id_projeto: int) -> int:
        return self.repo.create(id_aluno=id_aluno, id_projeto=id_projeto)
