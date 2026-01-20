from dataclasses import dataclass
from typing import List, Dict

from app.core.ports.input.porta_listar_selecionados import (
    ListarSelecionadosQuery,
    IListarSelecionadosProjetoInputPort,
)
from app.core.ports.output.porta_upd_aluno_projeto import IProjetoGateway


@dataclass
class ListarSelecionadosProjetoUseCase(IListarSelecionadosProjetoInputPort):
    projeto_gateway: IProjetoGateway

    def execute(self, query: ListarSelecionadosQuery) -> List[Dict]:
        id_projeto = query.id_projeto

        if not self.projeto_gateway.projeto_existe(id_projeto):
            raise ValueError("Projeto não encontrado.")

        return self.projeto_gateway.listar_alunos_ativos_detalhado(id_projeto)
