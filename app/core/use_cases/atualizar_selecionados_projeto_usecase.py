from dataclasses import dataclass
from typing import List, Set

from app.core.ports.input.porta_atualizar_selecionados import (
    AtualizarSelecionadosCommand,
    IAtualizarSelecionadosProjetoInputPort,
)
from app.core.ports.output.porta_inscricao_repository import IInscricaoRepository
from app.core.ports.output.porta_upd_aluno_projeto import IProjetoGateway
from app.core.ports.output.porta_aluno_repository import IAlunoRepository


@dataclass
class AtualizarSelecionadosProjetoUseCase(IAtualizarSelecionadosProjetoInputPort):
    projeto_gateway: IProjetoGateway
    aluno_repo: IAlunoRepository
    inscricao_repo: IInscricaoRepository
    max_selecionados: int = 4
    exigir_inscricao: bool = True
    impedir_duplo_ativo: bool = True

    def execute(self, command: AtualizarSelecionadosCommand) -> dict:
        id_projeto = command.id_projeto
        novos: List[int] = command.id_alunos_selecionados or []

        # 1) Validar projeto
        if not self.projeto_gateway.projeto_existe(id_projeto):
            raise ValueError("Projeto não encontrado.")

        # 2) Normalizar/validar lista (remove duplicados preservando ordem)
        vistos: Set[int] = set()
        novos_unicos: List[int] = []
        for a in novos:
            if a not in vistos:
                vistos.add(a)
                novos_unicos.append(a)

        # 3) Validar limite
        if len(novos_unicos) > self.max_selecionados:
            raise ValueError(f"Você só pode selecionar até {self.max_selecionados} alunos.")

        # 4) Validar inscrição (selecionar só quem se inscreveu)
        if self.exigir_inscricao:
            for id_aluno in novos_unicos:
                if not self.inscricao_repo.existe_inscricao(id_projeto=id_projeto, id_aluno=id_aluno):
                    raise ValueError(f"Aluno {id_aluno} não está inscrito neste projeto.")

        # 5) Buscar ativos atuais e calcular delta
        ativos_atuais = set(self.projeto_gateway.listar_ids_alunos_ativos(id_projeto))
        novos_set = set(novos_unicos)

        entrando = list(novos_set - ativos_atuais)
        saindo = list(ativos_atuais - novos_set)

        for id_aluno in entrando:
            status_aluno = self.aluno_repo.get_status(id_aluno)

            if status_aluno != "APROVADO":
                raise ValueError(
                    f"Aluno {id_aluno} não pode ser selecionado. "
                    f"Status atual: {status_aluno}. "
                    "Somente alunos APROVADOS podem participar de projetos."
                )

        for id_aluno in saindo:
            self.projeto_gateway.set_status_aluno(
                id_projeto=id_projeto,
                id_aluno=id_aluno,
                status=False
            )

            try:
                self.aluno_repo.update_status(id_aluno, "INADIMPLENTE")
            except ValueError:
                # aluno não existe mais no cadastro, ignora
                pass

        # 6) Regra: aluno não pode ficar ATIVO em dois projetos ao mesmo tempo (opcional)
        if self.impedir_duplo_ativo:
            for id_aluno in entrando:
                if self.projeto_gateway.aluno_ativo_em_outro_projeto(id_aluno=id_aluno, id_projeto_atual=id_projeto):
                    raise ValueError(f"Aluno {id_aluno} já está selecionado em outro projeto.")

        # 7) Aplicar mudanças (estado, sem DELETE)
        for id_aluno in entrando:
            self.projeto_gateway.upsert_status_aluno(id_projeto=id_projeto, id_aluno=id_aluno, status=True)

        for id_aluno in saindo:
            self.projeto_gateway.set_status_aluno(id_projeto=id_projeto, id_aluno=id_aluno, status=False)

        return {
            "id_projeto": id_projeto,
            "selecionados": novos_unicos,   # estado final desejado
            "entraram": entrando,
            "sairam": saindo,
        }
