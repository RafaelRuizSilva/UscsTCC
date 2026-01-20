# app/core/ports/output/porta_tipo_bolsa_repository.py
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from app.core.models.tipo_bolsa import TipoBolsaCreate

class ITipoBolsaRepository(ABC):
    @abstractmethod
    def create(self, data: TipoBolsaCreate) -> int: ...
    @abstractmethod
    def list_all(self, limit: int, offset: int) -> List[Dict]: ...
    @abstractmethod
    def delete_by_id(self, id_tipo_bolsa: int) -> int: ...
    @abstractmethod
    def get_by_id(self, id_tipo_bolsa: int) -> Optional[Dict]: ...
