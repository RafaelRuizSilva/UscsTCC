# app/core/use_cases/create_notificacao_usecase.py
from datetime import datetime
from typing import Optional
from app.core.models.notificacao import NotificacaoCreate, Notificacao
from app.core.ports.output.porta_notificacao_repository import INotificacaoRepository
from app.adapters.message.rabbit_publisher import RabbitPublisher

class CreateNotificacaoUseCase:
    def __init__(self, repo: INotificacaoRepository, publisher: Optional[RabbitPublisher] = None):
        self.repo = repo
        self.publisher = publisher  # opcional

    def execute(self, notificacao_data: NotificacaoCreate, publicar: bool = False) -> int:
        notificacao = Notificacao(
            tipo=notificacao_data.tipo,
            mensagem=notificacao_data.mensagem,
            destinatario=notificacao_data.destinatario,
            lida=False,
            data_criacao=datetime.now(),
        )
        if publicar and self.publisher:
            self.publisher.publish(notificacao.dict())
        return self.repo.salvar(notificacao)
