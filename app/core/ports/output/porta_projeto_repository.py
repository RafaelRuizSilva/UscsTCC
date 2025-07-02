from abc import ABC, abstractmethod
from app.core.models.projeto import Projeto

class IProjetoRepository(ABC):
    @abstractmethod
    def create(self, projeto: Projeto) -> int:
        pass
