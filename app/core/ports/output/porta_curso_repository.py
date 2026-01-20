from abc import ABC, abstractmethod
from app.core.models.curso import Curso

class ICursoRepository(ABC):
    @abstractmethod
    def create(self, curso: Curso) -> int:
        pass

    @abstractmethod
    def get_all(self) -> list[dict]:
        pass

    @abstractmethod
    def get_by_id(self, curso_id: int) -> dict:
        pass

    @abstractmethod
    def update(self, curso_id: int, curso: Curso) -> None:
        pass

    @abstractmethod
    def delete(self, curso_id: int) -> None:
        pass