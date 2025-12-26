from abc import ABC, abstractmethod
from app.core.models.aluno import Aluno
from typing import Sequence

class IAlunoRepository(ABC):
    @abstractmethod
    def create(self, aluno: Aluno, pdf_bytes: bytes) -> int: ...

    @abstractmethod
    def list_all(self) -> list[dict]: ...

    @abstractmethod
    def get_by_id(self, aluno_id: int) -> dict | None: ...

    @abstractmethod
    def delete(self, aluno_id: int) -> None: ...

    # ✅ NOVO
    @abstractmethod
    def update_status(self, aluno_id: int, novo_status: str) -> None: ...

    @abstractmethod
    def update_status_many_reprovado(self, aluno_ids: Sequence[int]) -> int:
        """Marca vários alunos como REPROVADO (com inadimplente_ate +2 anos). Retorna total afetado."""
        pass

    @abstractmethod
    def get_status(self, id_aluno: int) -> str:
        ...