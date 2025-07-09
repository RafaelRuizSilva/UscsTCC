from fastapi import APIRouter, Depends, HTTPException
from app.dependencies.db import get_db_conn
from app.core.security import get_current_user
from app.adapters.repositories.inscricao_repository import InscricaoRepository
from app.core.use_cases.create_inscricao_usecase import CriarInscricaoUseCase
from app.core.models.inscricao import InscricaoCreate

router = APIRouter()

@router.post("/inscrever")
def inscrever(inscricao: InscricaoCreate,
              db=Depends(get_db_conn),
              id_aluno: int = Depends(get_current_user("aluno"))):
    try:
        repo = InscricaoRepository(db)
        use_case = CriarInscricaoUseCase(repo)
        id_inscricao = use_case.execute(id_aluno, inscricao.id_projeto)

        return {
            "success": True,
            "message": "Inscrição realizada com sucesso!",
            "data": {"id_inscricao": id_inscricao}
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno no servidor")
