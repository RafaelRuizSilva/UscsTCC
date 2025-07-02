from fastapi import APIRouter, Depends, HTTPException
from app.core.models.projeto import Projeto
from app.adapters.repositories.projeto_repository import ProjetoRepository
from app.core.use_cases.create_projeto_usecase import CreateProjetoUseCase
from app.dependencies import get_db_conn

router = APIRouter(prefix="/projetos", tags=["Projetos"])

@router.post("/")
def cadastrar_projeto(projeto: Projeto, db=Depends(get_db_conn)):
    repo = ProjetoRepository(db)
    usecase = CreateProjetoUseCase(repo)
    try:
        projeto_id = usecase.execute(projeto)
        return {"id": projeto_id, "mensagem": "Projeto cadastrado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Erro inesperado")


