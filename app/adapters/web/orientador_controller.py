from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from app.core.models.orientador import Orientador
from app.core.models.orientador_out import OrientadorOut
from app.adapters.repositories.orientador_repository import OrientadorRepository
from app.core.use_cases.create_orientador_usecase import CreateOrientadorUseCase
from app.core.use_cases.listar_todos_orientadores_usecase import ListarTodosOrientadoresUseCase
from app.core.use_cases.obter_orientador_por_id_usecase import ObterOrientadorPorIdUseCase
from app.core.use_cases.obter_orientador_por_nome_usecase import ObterOrientadorPorNomeUseCase
from app.dependencies import get_db_conn
from app.core.security import get_current_user

router = APIRouter(prefix="/orientadores", tags=["Orientadores"])

# ---------- CREATE ----------
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

# ---------- AUTH (já existente) ----------
@router.get("/painel-orientador")
def painel(user_id: int = Depends(get_current_user("orientador"))):
    return {"msg": f"Orientador autenticado: ID {user_id}"}

# ---------- READS ----------
@router.get("/", response_model=List[OrientadorOut])
def listar_todos_orientadores(db=Depends(get_db_conn)):
    repo = OrientadorRepository(db)
    usecase = ListarTodosOrientadoresUseCase(repo)
    return usecase.execute()

# ⬇️ MANTER /buscar ANTES DE /{id}
@router.get("/buscar", response_model=OrientadorOut)
def obter_orientador_por_nome(
    nome: str = Query(..., min_length=1),
    db=Depends(get_db_conn)
):
    repo = OrientadorRepository(db)
    usecase = ObterOrientadorPorNomeUseCase(repo)
    result = usecase.execute(nome)
    if not result:
        raise HTTPException(status_code=404, detail="Orientador não encontrado pelo nome informado")
    return result

@router.get("/{id}", response_model=OrientadorOut)
def obter_orientador_por_id(
    id: int = Path(..., ge=1),
    db=Depends(get_db_conn)
):
    repo = OrientadorRepository(db)
    usecase = ObterOrientadorPorIdUseCase(repo)
    result = usecase.execute(id)
    if not result:
        raise HTTPException(status_code=404, detail="Orientador não encontrado")
    return result
