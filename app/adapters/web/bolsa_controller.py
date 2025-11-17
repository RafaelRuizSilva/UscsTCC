# app/controllers/bolsa_controller.py
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from app.dependencies.db import get_db_conn
from app.core.security import get_current_user
from app.adapters.repositories.bolsa_repository import BolsaRepository
from app.core.use_cases.bolsa_create_usecase import CreateBolsaUseCase
from app.core.use_cases.bolsa_delete_usecase import DeleteBolsaUseCase
from app.core.use_cases.bolsa_list_usecase import ListBolsasUseCase
from app.core.use_cases.bolsa_get_by_id_usecase import GetBolsaByIdUseCase
from app.core.models.bolsa import BolsaCreate

router = APIRouter(prefix="/bolsas", tags=["Bolsas"])

def get_repo(db=Depends(get_db_conn)):
    return BolsaRepository(db)

@router.post("/", status_code=status.HTTP_201_CREATED)
def criar_bolsa(
    body: BolsaCreate,
    repo: Annotated[BolsaRepository, Depends(get_repo)],
    _sec: int = Depends(get_current_user("secretaria")),
):
    try:
        new_id = CreateBolsaUseCase(repo).execute(body)
        return {"id_bolsa": new_id, "mensagem": "Bolsa atribuída ao aluno"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", status_code=status.HTTP_200_OK)
def listar_bolsas(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    repo: Annotated[BolsaRepository, Depends(get_repo)] = None,
    _sec: int = Depends(get_current_user("secretaria")),
):
    try:
        data = ListBolsasUseCase(repo).execute(limit, offset)
        return {"bolsas": data, "limit": limit, "offset": offset, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar bolsas: {e}")

@router.get("/{id_bolsa}", status_code=status.HTTP_200_OK)
def obter_bolsa_por_id(
    id_bolsa: int = Path(..., ge=1),
    repo: Annotated[BolsaRepository, Depends(get_repo)] = None,
    _sec: int = Depends(get_current_user("secretaria")),
):
    data = GetBolsaByIdUseCase(repo).execute(id_bolsa)
    if not data:
        raise HTTPException(status_code=404, detail="Bolsa não encontrada")
    return data

@router.delete("/{id_bolsa}", status_code=status.HTTP_200_OK)
def remover_bolsa(
    id_bolsa: int = Path(..., ge=1),
    repo: Annotated[BolsaRepository, Depends(get_repo)] = None,
    _sec: int = Depends(get_current_user("secretaria")),
):
    try:
        DeleteBolsaUseCase(repo).execute(id_bolsa)
        return {"mensagem": "Bolsa removida com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
