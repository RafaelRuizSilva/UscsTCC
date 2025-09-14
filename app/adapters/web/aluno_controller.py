from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.db import get_db_conn
from app.adapters.repositories.aluno_repository import AlunoRepository
from app.core.ports.output.porta_aluno_repository import IAlunoRepository
from app.core.models.aluno import Aluno
from app.core.security import get_current_user  # já utilizado por você

from app.core.use_cases.create_aluno_usecase import CreateAlunoUseCase
from app.core.use_cases.list_alunos_usecase import ListAlunosUseCase
from app.core.use_cases.delete_alunos_usecase import DeleteAlunoUseCase
from app.core.use_cases.get_aluno_usecase import GetAlunoByIdUseCase
from app.core.use_cases.aprovar_aluno_usecase import AprovarAlunoUseCase

router = APIRouter(prefix="/alunos", tags=["Alunos"])

# DI mínima do repo
def get_repo(db=Depends(get_db_conn)) -> IAlunoRepository:
    return AlunoRepository(db)

@router.put("/{aluno_id}/aprovar", status_code=status.HTTP_200_OK)
def aprovar_aluno(
    aluno_id: int,
    repo: Annotated[IAlunoRepository, Depends(get_repo)],
):
    uc = AprovarAlunoUseCase(repo)
    try:
        uc.execute(aluno_id)
        return {"mensagem": "Aluno aprovado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao aprovar aluno")

@router.post("/", status_code=status.HTTP_201_CREATED)
def cadastrar_aluno(
    aluno: Aluno,
    repo: Annotated[IAlunoRepository, Depends(get_repo)],
):
    usecase = CreateAlunoUseCase(repo)
    try:
        aluno_id = usecase.execute(aluno)
        return {"id": aluno_id, "mensagem": "Aluno cadastrado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro inesperado")

# --- Exemplo de rota protegida ---
@router.get("/painel-aluno")
def me(user_id: int = Depends(get_current_user("aluno"))):
    return {"msg": f"Aluno autenticado: ID {user_id}"}

# --------- GET ALL (List) ----------
@router.get("/", status_code=status.HTTP_200_OK)
def listar_alunos(
    repo: Annotated[IAlunoRepository, Depends(get_repo)],
):
    usecase = ListAlunosUseCase(repo)
    try:
        return usecase.execute()
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao listar alunos")

@router.get("/{aluno_id}", status_code=status.HTTP_200_OK)
def obter_aluno_por_id(
    aluno_id: int,
    repo: Annotated[IAlunoRepository, Depends(get_repo)],
):
    uc = GetAlunoByIdUseCase(repo)
    try:
        data = uc.execute(aluno_id)
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado.")
        return data
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao buscar aluno.")

# --------- DELETE by ID ----------
@router.delete("/{aluno_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_aluno(
    aluno_id: int,
    repo: Annotated[IAlunoRepository, Depends(get_repo)],
):
    usecase = DeleteAlunoUseCase(repo)
    try:
        usecase.execute(aluno_id)
        # 204: sem corpo de resposta
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao excluir aluno")

