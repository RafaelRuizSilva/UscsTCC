from abc import ABC, abstractmethod

class IInscricaoRepository(ABC):
    @abstractmethod
    def create(self, id_aluno: int, id_projeto: int) -> int:
        pass

    @abstractmethod
    def list_all(self) -> list[dict]:  # Para listar todas as inscrições
        pass

    @abstractmethod
    def get_by_id(self, id_inscricao: int) -> dict | None:  # Para obter uma inscrição por ID
        pass

    @abstractmethod
    def delete(self, id_inscricao: int) -> None:  # Para excluir uma inscrição por ID
        pass
