# app/adapters/web/notificacao_controller.py
from fastapi import APIRouter, Depends, HTTPException, Query
from app.dependencies.db import get_db_conn
from app.adapters.repositories.notificacao_repository import NotificacaoRepository
from app.core.models.notificacao import NotificacaoCreate
from app.core.use_cases.create_notificacao_usecase import CreateNotificacaoUseCase

router = APIRouter(prefix="/notificacoes", tags=["Notificações"])

@router.post("/")
def criar_notificacao(payload: NotificacaoCreate, db=Depends(get_db_conn)):
    try:
        repo = NotificacaoRepository(db)
        usecase = CreateNotificacaoUseCase(repo)  # sem publisher
        nova_id = usecase.execute(payload, publicar=False)
        return {"mensagem": "Notificação criada com sucesso", "id": nova_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
def listar_notificacoes(
    destinatario: str = Query(..., min_length=3),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db=Depends(get_db_conn),
):
    try:
        repo = NotificacaoRepository(db)
        items, total = repo.listar_por_destinatario(destinatario, page, size)
        return {"items": items, "page": page, "size": size, "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/mark-all")
def marcar_todas_como_lidas(destinatario: str = Query(..., min_length=3), db=Depends(get_db_conn)):
    try:
        repo = NotificacaoRepository(db)
        qtd = repo.marcar_todas_lidas(destinatario)
        return {"mensagem": f"{qtd} notificações marcadas como lidas"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
