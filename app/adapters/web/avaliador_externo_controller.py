from fastapi import APIRouter, Depends, HTTPException
from app.core.models.avaliador_externo import AvaliadorExternoCreate
from app.adapters.repositories.avaliador_externo_repository import AvaliadorExternoRepository
from app.core.use_cases.create_avaliador_externo_usecase import CreateAvaliadorExternoUseCase
from app.dependencies.db import get_db_conn

router = APIRouter()

@router.post("/avaliadores-externos")
def cadastrar_avaliador_externo(
    avaliador: AvaliadorExternoCreate,
    db=Depends(get_db_conn)
):
    repo = AvaliadorExternoRepository(db)
    use_case = CreateAvaliadorExternoUseCase(repo)

    try:
        id_gerado = use_case.execute(avaliador)
        return {"success": True, "id_avaliador": id_gerado}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Erro interno ao cadastrar avaliador.")
