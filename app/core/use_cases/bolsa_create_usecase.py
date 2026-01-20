# app/core/use_cases/bolsa_create_usecase.py
from app.core.ports.output.porta_bolsa_repository import IBolsaRepository
from app.core.models.bolsa import BolsaCreate

class CreateBolsaUseCase:
    def __init__(self, repo: IBolsaRepository):
        self.repo = repo
    def execute(self, data: BolsaCreate) -> int:
        return self.repo.create(data)
