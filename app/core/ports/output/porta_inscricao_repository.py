from abc import ABC, abstractmethod

class IInscricaoRepository(ABC):
    @abstractmethod
    def create(self, id_aluno: int, id_projeto: int) -> int:
        pass
