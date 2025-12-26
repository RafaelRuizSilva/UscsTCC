from app.core.ports.output.porta_upd_aluno_projeto import IProjetoGateway


class GetProjetoSelecionadoAlunoUseCase:
    def __init__(self, projeto_gateway: IProjetoGateway):
        self.projeto_gateway = projeto_gateway

    def execute(self, id_aluno: int):
        projeto = self.projeto_gateway.get_projeto_selecionado_completo_por_aluno(id_aluno)

        if not projeto:
            raise ValueError("Aluno não está selecionado em nenhum projeto.")

        return projeto
