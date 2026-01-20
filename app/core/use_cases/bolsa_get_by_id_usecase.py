# app/core/use_cases/bolsa_get_by_id_usecase.py
from typing import Optional, Dict
from app.core.ports.output.porta_bolsa_repository import IBolsaRepository

class GetBolsaByIdUseCase:
    def __init__(self, repo: IBolsaRepository):
        self.repo = repo
    def execute(self, id_bolsa: int) -> Optional[Dict]:
        return self.repo.get_by_id(id_bolsa)
