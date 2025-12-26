from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class ListarSelecionadosQuery:
    id_projeto: int


class IListarSelecionadosProjetoInputPort(ABC):
    @abstractmethod
    def execute(self, query: ListarSelecionadosQuery) -> List[Dict]:
        ...
