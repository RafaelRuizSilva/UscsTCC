from fastapi import APIRouter, Depends, HTTPException
from app.dependencies.db import get_db_conn
from app.core.models.notificacao import NotificacaoCreate
from app.adapters.repositories.notificacao_repository import NotificacaoRepository
from app.adapters.message.rabbit_publisher import RabbitPublisher
from app.core.use_cases.create_notificacao_usecase import CreateNotificacaoUseCase

router = APIRouter()

@router.post("/notificacoes")
def criar_notificacao(payload: NotificacaoCreate, db=Depends(get_db_conn)):
    try:
        repo = NotificacaoRepository(db)
        publisher = RabbitPublisher()
        usecase = CreateNotificacaoUseCase(repo, publisher)
        nova_id = usecase.execute(payload)
        return {"mensagem": "Notificação criada com sucesso", "id": nova_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
