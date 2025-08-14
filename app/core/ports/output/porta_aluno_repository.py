from abc import ABC, abstractmethod
from app.core.models.aluno import Aluno

class IAlunoRepository(ABC):
    @abstractmethod
    def create(self, aluno: Aluno) -> int: ...

    @abstractmethod
    def list_all(self) -> list[dict]: ...

    @abstractmethod
    def get_by_id(self, aluno_id: int) -> dict | None: ...

    @abstractmethod
    def delete(self, aluno_id: int) -> None: ...
