from abc import ABC, abstractmethod
from app.core.models.campus import Campus

class ICampusRepository(ABC):
    @abstractmethod
    def create(self, campus: Campus) -> int:
        pass

    @abstractmethod
    def get_all(self) -> list[dict]:
        pass
