from fastapi import APIRouter, Depends, HTTPException
from app.core.models.aluno import Aluno
from app.adapters.repositories.aluno_repository import AlunoRepository
from app.core.use_cases.create_aluno_usecase import CreateAlunoUseCase
from app.dependencies import get_db_conn
from app.core.security import get_current_user

router = APIRouter(prefix="/alunos", tags=["Alunos"])

@router.post("/")
def cadastrar_aluno(aluno: Aluno, db=Depends(get_db_conn)):
    repo = AlunoRepository(db)
    usecase = CreateAlunoUseCase(repo)
    try:
        aluno_id = usecase.execute(aluno)
        return {"id": aluno_id, "mensagem": "Aluno cadastrado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Erro inesperado")

# --- Exemplo de rota protegida ---
@router.get("/painel-aluno")
def me(user_id: int = Depends(get_current_user("aluno"))):
    return {"msg": f"Aluno autenticado: ID {user_id}"}


