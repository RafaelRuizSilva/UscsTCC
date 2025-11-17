# app/controllers/tipo_bolsa_controller.py
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from app.dependencies.db import get_db_conn
from app.core.security import get_current_user
from app.adapters.repositories.tipo_bolsa_repository import TipoBolsaRepository
from app.core.use_cases.tipo_bolsa_create_usecase import CreateTipoBolsaUseCase
from app.core.use_cases.tipo_bolsa_list_usecase import ListTipoBolsaUseCase
from app.core.use_cases.tipo_bolsa_delete_usecase import DeleteTipoBolsaUseCase
from app.core.models.tipo_bolsa import TipoBolsaCreate, TipoBolsaOut

router = APIRouter(prefix="/tipos-bolsa", tags=["Tipos de Bolsa"])

def get_repo(db=Depends(get_db_conn)):
    return TipoBolsaRepository(db)

@router.post("/", status_code=status.HTTP_201_CREATED)
def criar_tipo_bolsa(
    body: TipoBolsaCreate,
    repo: Annotated[TipoBolsaRepository, Depends(get_repo)],
    _sec: int = Depends(get_current_user("secretaria")),
):
    try:
        new_id = CreateTipoBolsaUseCase(repo).execute(body)
        return {"id_tipo_bolsa": new_id, "mensagem": "Tipo de bolsa criado"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[TipoBolsaOut])
def listar_tipos_bolsa(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    repo: Annotated[TipoBolsaRepository, Depends(get_repo)] = None,
):
    return ListTipoBolsaUseCase(repo).execute(limit, offset)

@router.delete("/{id_tipo_bolsa}", status_code=status.HTTP_200_OK)
def deletar_tipo_bolsa(
    id_tipo_bolsa: int = Path(..., ge=1),
    repo: Annotated[TipoBolsaRepository, Depends(get_repo)] = None,
    _sec: int = Depends(get_current_user("secretaria")),
):
    try:
        DeleteTipoBolsaUseCase(repo).execute(id_tipo_bolsa)
        return {"mensagem": "Tipo de bolsa removido"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
