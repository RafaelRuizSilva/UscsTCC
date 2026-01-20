from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated
from app.dependencies.db import get_db_conn
from app.adapters.repositories.projeto_repository import ProjetoRepository
from app.core.use_cases.list_all_envios_usecase import ListarEnviosUseCase
from app.core.use_cases.list_envio_by_id_usecase import ObterEnvioPorIdUseCase
from app.core.security import get_current_user

router = APIRouter(prefix="/envios", tags=["Envios de Projetos"])

@router.get("/", response_model=list)
def get_all_envios(db=Depends(get_db_conn),
                   id_secretaria: int = Depends(get_current_user("secretaria"))):
    try:
        repo = ProjetoRepository(db)
        usecase = ListarEnviosUseCase(repo)
        envios = usecase.execute()

        return envios
    except Exception:
        raise HTTPException(status_code=500, detail=f"Erro ao listar envios.")

@router.get("/{id_envio}", response_model=dict)
def get_envio_by_id(id_envio: int, db=Depends(get_db_conn),
                    id_secretaria: int = Depends(get_current_user("secretaria"))):
    try:
        repo = ProjetoRepository(db)
        usecase = ObterEnvioPorIdUseCase(repo)
        envio = usecase.execute(id_envio)
        if not envio:
            raise HTTPException(status_code=404, detail="Envio não encontrado.")
        return envio
    except Exception:
        raise HTTPException(status_code=500, detail="Erro ao obter envio.")
