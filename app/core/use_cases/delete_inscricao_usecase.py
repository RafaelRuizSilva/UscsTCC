# app/core/usecases/inscricao/excluir_inscricao.py
from app.core.ports.output.porta_inscricao_repository import IInscricaoRepository

class ExcluirInscricaoUseCase:
    def __init__(self, repo: IInscricaoRepository):
        self.repo = repo

    def execute(self, id_inscricao: int) -> None:
        self.repo.delete(id_inscricao)
