from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.models.avaliador_externo import AvaliadorExternoCreate
from app.core.ports.output.porta_avaliador_externo_repository import IAvaliadorExternoRepository
from app.dependencies.db import get_db_conn
from app.adapters.repositories.avaliador_externo_repository import AvaliadorExternoRepository

from app.core.use_cases.create_avaliador_externo_usecase import CreateAvaliadorExternoUseCase
from app.core.use_cases.list_avaliador_externo_usecase import ListAvaliadorExternoUseCase
from app.core.use_cases.get_avaliador_externo_usecase import GetAvaliadorExternoUseCase
from app.core.use_cases.update_avaliador_externo_usecase import UpdateAvaliadorExternoUseCase
from app.core.use_cases.delete_avaliador_externo_usecase import DeleteAvaliadorExternoUseCase
from app.core.security import get_current_user

router = APIRouter(prefix="/avaliadores-externos", tags=["AvaliadoresExternos"])

# Injeção mínima do repositório
def get_repo(db=Depends(get_db_conn)) -> IAvaliadorExternoRepository:
    return AvaliadorExternoRepository(db)

# -------------------- CREATE --------------------
@router.post("", status_code=status.HTTP_201_CREATED)
def cadastrar_avaliador_externo(
    avaliador: AvaliadorExternoCreate,
    repo: Annotated[IAvaliadorExternoRepository, Depends(get_repo)],
    id_secretaria: int = Depends(get_current_user("secretaria"))
):
    use_case = CreateAvaliadorExternoUseCase(repo)
    try:
        new_id = use_case.execute(avaliador)
        return {"id_avaliador": new_id}
    except ValueError as e:
        msg = str(e).lower()
        if "cadastrado" in msg or "duplicate" in msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao cadastrar avaliador.")

# -------------------- READ (LIST) --------------------
@router.get("", status_code=status.HTTP_200_OK)
def listar_avaliadores_externos(
    repo: Annotated[IAvaliadorExternoRepository, Depends(get_repo)],
    id_secretaria: int = Depends(get_current_user("secretaria"))
):
    use_case = ListAvaliadorExternoUseCase(repo)
    try:
        return use_case.execute()
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao listar avaliadores.")

# -------------------- READ (BY ID) --------------------
@router.get("/{id_avaliador}", status_code=status.HTTP_200_OK)
def obter_avaliador_externo(
    id_avaliador: int,
    repo: Annotated[IAvaliadorExternoRepository, Depends(get_repo)],
    id_secretaria: int = Depends(get_current_user("secretaria"))
):
    use_case = GetAvaliadorExternoUseCase(repo)
    try:
        data = use_case.execute(id_avaliador)
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avaliador não encontrado.")
        return data
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao buscar avaliador.")

# -------------------- UPDATE --------------------
@router.put("/{id_avaliador}", status_code=status.HTTP_204_NO_CONTENT)
def atualizar_avaliador_externo(
    id_avaliador: int,
    avaliador: AvaliadorExternoCreate,
    repo: Annotated[IAvaliadorExternoRepository, Depends(get_repo)],
    id_secretaria: int = Depends(get_current_user("secretaria"))
):
    use_case = UpdateAvaliadorExternoUseCase(repo)
    try:
        use_case.execute(id_avaliador, avaliador)
    except ValueError as e:
        msg = str(e).lower()
        if "cadastrado" in msg or "duplicate" in msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao atualizar avaliador.")

# -------------------- DELETE --------------------
@router.delete("/{id_avaliador}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_avaliador_externo(
    id_avaliador: int,
    repo: Annotated[IAvaliadorExternoRepository, Depends(get_repo)],
    id_secretaria: int = Depends(get_current_user("secretaria"))
):
    use_case = DeleteAvaliadorExternoUseCase(repo)
    try:
        use_case.execute(id_avaliador)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao excluir avaliador.")
