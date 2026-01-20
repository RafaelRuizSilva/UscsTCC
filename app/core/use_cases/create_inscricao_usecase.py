from app.core.ports.output.porta_inscricao_repository import IInscricaoRepository
from app.core.ports.output.porta_aluno_repository import IAlunoRepository
from app.core.ports.output.porta_upd_aluno_projeto import IProjetoGateway

class CriarInscricaoUseCase:
    def __init__(
        self,
        inscricao_repo: IInscricaoRepository,
        aluno_repo: IAlunoRepository,
        projeto_gateway: IProjetoGateway,
    ):
        self.inscricao_repo = inscricao_repo
        self.aluno_repo = aluno_repo
        self.projeto_gateway = projeto_gateway

    def execute(self, id_aluno: int, id_projeto: int) -> int:
        # 1) Status do aluno
        status_aluno = self.aluno_repo.get_status(id_aluno)
        if status_aluno != "APROVADO":
            raise ValueError(
                f"Aluno não pode se inscrever. Status atual: {status_aluno}."
            )

        # 2) 🔒 NOVA REGRA: aluno já ativo em projeto
        if self.projeto_gateway.aluno_ativo_em_outro_projeto(
            id_aluno=id_aluno,
            id_projeto_atual=id_projeto,
        ):
            raise ValueError(
                "Aluno já está selecionado em um projeto e não pode se inscrever em outro."
            )

        return self.inscricao_repo.create(id_aluno, id_projeto)
