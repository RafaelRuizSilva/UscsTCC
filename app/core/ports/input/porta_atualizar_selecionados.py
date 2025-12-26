from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class AtualizarSelecionadosCommand:
    id_projeto: int
    id_alunos_selecionados: List[int]


class IAtualizarSelecionadosProjetoInputPort(ABC):
    @abstractmethod
    def execute(self, command: AtualizarSelecionadosCommand) -> dict:
        ...
