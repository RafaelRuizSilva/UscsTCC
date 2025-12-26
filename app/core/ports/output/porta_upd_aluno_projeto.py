from abc import ABC, abstractmethod
from typing import List, Dict

class IProjetoGateway(ABC):
    @abstractmethod
    def projeto_existe(self, id_projeto: int) -> bool:
        ...

    @abstractmethod
    def listar_ids_alunos_ativos(self, id_projeto: int) -> List[int]:
        ...

    @abstractmethod
    def upsert_status_aluno(self, id_projeto: int, id_aluno: int, status: bool) -> None:
        ...

    @abstractmethod
    def set_status_aluno(self, id_projeto: int, id_aluno: int, status: bool) -> None:
        ...

    @abstractmethod
    def aluno_ativo_em_outro_projeto(self, id_aluno: int, id_projeto_atual: int) -> bool:
        ...

    @abstractmethod
    def listar_alunos_ativos_detalhado(self, id_projeto: int) -> List[Dict]:
        ...