from fastapi import APIRouter, Depends, HTTPException
from app.core.models.orientador import Orientador
from app.adapters.repositories.orientador_repository import OrientadorRepository
from app.core.use_cases.create_orientador_usecase import CreateOrientadorUseCase
from app.dependencies import get_db_conn

router = APIRouter(prefix="/orientadores", tags=["Orientadores"])

@router.post("/")
def cadastrar_orientador(orientador: Orientador, db=Depends(get_db_conn)):
    repo = OrientadorRepository(db)
    usecase = CreateOrientadorUseCase(repo)
    try:
        orientador_id = usecase.execute(orientador)
        return {"id": orientador_id, "mensagem": "Orientador cadastrado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Erro inesperado")


