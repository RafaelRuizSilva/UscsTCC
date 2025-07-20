from abc import ABC, abstractmethod
from app.core.models.avaliador_externo import AvaliadorExternoCreate

class IAvaliadorExternoRepository(ABC):
    @abstractmethod
    def create(self, avaliador: AvaliadorExternoCreate) -> int:
        pass
