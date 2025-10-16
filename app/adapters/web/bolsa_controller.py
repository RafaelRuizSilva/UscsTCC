from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Path
from app.dependencies.db import get_db_conn
from app.core.ports.output.porta_bolsa_repository import IBolsaRepository
from app.adapters.repositories.bolsa_repository import BolsaRepository
from app.core.use_cases.list_bolsas_usecase import ListBolsasUseCase
from app.core.use_cases.set_bolsa_status_usecase import SetBolsaStatusUseCase
from pydantic import BaseModel, Field
from app.core.use_cases.create_bolsa_usecase import CreateBolsaUseCase


class BolsaUpdateDTO(BaseModel):
    possui_bolsa: bool

class BolsaCreateDTO(BaseModel):
    id_aluno: int = Field(..., ge=1)
    possui_bolsa: bool = Field(..., description="True se for bolsista")

router = APIRouter(prefix="/bolsas", tags=["Bolsas"])

def get_repo(db=Depends(get_db_conn)) -> IBolsaRepository:
    return BolsaRepository(db)

@router.get("/", status_code=status.HTTP_200_OK)
def listar_bolsas(repo: Annotated[IBolsaRepository, Depends(get_repo)]):
    try:
        uc = ListBolsasUseCase(repo)
        return uc.execute()
    except Exception:
        raise HTTPException(status_code=500, detail="Erro ao listar bolsas")

@router.post("/", status_code=status.HTTP_201_CREATED)
def criar_bolsa(
    body: BolsaCreateDTO,
    repo: Annotated[IBolsaRepository, Depends(get_repo)]
):
    try:
        id_bolsa = CreateBolsaUseCase(repo).execute(body.id_aluno, body.possui_bolsa)
        return {"id_bolsa": id_bolsa, "id_aluno": body.id_aluno, "possui_bolsa": body.possui_bolsa}
    except ValueError as e:
        # duplicate / fk inválida
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Erro ao cadastrar bolsa")


@router.put("/{id_aluno}", status_code=status.HTTP_200_OK)
def atualizar_bolsa(
    id_aluno: int = Path(..., ge=1),
    body: BolsaUpdateDTO = ...,
    repo: Annotated[IBolsaRepository, Depends(get_repo)] = None,
):
    try:
        uc = SetBolsaStatusUseCase(repo)
        uc.execute(id_aluno, body.possui_bolsa)
        return {"id_aluno": id_aluno, "possui_bolsa": body.possui_bolsa}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Erro ao atualizar bolsa")
