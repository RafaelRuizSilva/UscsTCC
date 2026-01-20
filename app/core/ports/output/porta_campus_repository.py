from abc import ABC, abstractmethod
from app.core.models.campus import Campus

class ICampusRepository(ABC):
    @abstractmethod
    def create(self, campus: Campus) -> int:
        pass

    @abstractmethod
    def get_all(self) -> list[dict]:
        pass

    @abstractmethod
    def get_by_id(self, campus_id: int) -> dict:
        pass

    @abstractmethod
    def update(self, campus_id: int, campus: Campus) -> None:
        pass

    @abstractmethod
    def delete(self, campus_id: int) -> None:
        pass