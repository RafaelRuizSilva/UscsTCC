from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from app.core.models.secretaria import Secretaria

class ISecretariaRepository(ABC):
    @abstractmethod
    def create(self, secretaria: Secretaria) -> int: ...

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Dict]: ...
