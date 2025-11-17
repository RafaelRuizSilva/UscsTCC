# app/core/use_cases/bolsa_delete_usecase.py
from app.core.ports.output.porta_bolsa_repository import IBolsaRepository

class DeleteBolsaUseCase:
    def __init__(self, repo: IBolsaRepository):
        self.repo = repo
    def execute(self, id_bolsa: int) -> None:
        affected = self.repo.delete_by_id(id_bolsa)
        if affected == 0:
            raise ValueError("Bolsa não encontrada.")
