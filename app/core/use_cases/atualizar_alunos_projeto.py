from app.core.models.upd_aluno_projeto_model import UpdateProjetoAlunosDTO
from app.core.ports.output.porta_upd_aluno_projeto import IProjetoGateway
from app.adapters.message.rabbit_publisher import RabbitPublisher

class UpdateProjetoAlunosUseCase:
    def __init__(self, gateway: IProjetoGateway):
        self.gateway = gateway

    def execute(self, dto: UpdateProjetoAlunosDTO):
        self.gateway.atualizar_alunos_projeto(dto.id_projeto, dto.id_alunos)