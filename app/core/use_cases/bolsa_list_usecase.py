# app/core/use_cases/bolsa_list_usecase.py
from typing import List, Dict
from app.core.ports.output.porta_bolsa_repository import IBolsaRepository

class ListBolsasUseCase:
    def __init__(self, repo: IBolsaRepository):
        self.repo = repo
    def execute(self, limit: int, offset: int) -> List[Dict]:
        return self.repo.list_all(limit, offset)
