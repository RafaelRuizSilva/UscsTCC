from abc import ABC, abstractmethod
from app.core.models.avaliador_externo import AvaliadorExternoCreate

class IAvaliadorExternoRepository(ABC):
    @abstractmethod
    def create(self, avaliador: AvaliadorExternoCreate) -> int:
        pass

    @abstractmethod
    def list_all(self) -> list[dict]:
        pass

    @abstractmethod
    def get_by_id(self, id_avaliador: int) -> dict | None:
        pass

    @abstractmethod
    def update(self, id_avaliador: int, avaliador: AvaliadorExternoCreate) -> None:
        pass

    @abstractmethod
    def delete(self, id_avaliador: int) -> None:
        pass