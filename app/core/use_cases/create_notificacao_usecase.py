from datetime import datetime
from app.core.models.notificacao import NotificacaoCreate, Notificacao
from app.core.ports.output.porta_notificacao_repository import INotificacaoRepository
from app.adapters.message.rabbit_publisher import RabbitPublisher

class CreateNotificacaoUseCase:
    def __init__(self, repo: INotificacaoRepository, publisher: RabbitPublisher):
        self.repo = repo
        self.publisher = publisher

    def execute(self, notificacao_data: NotificacaoCreate) -> int:
        notificacao = Notificacao(
            tipo=notificacao_data.tipo,
            mensagem=notificacao_data.mensagem,
            destinatario=notificacao_data.destinatario,
            lida=False,
            data_criacao=datetime.now()
        )
        self.publisher.publish(notificacao.dict())
        return self.repo.salvar(notificacao)
