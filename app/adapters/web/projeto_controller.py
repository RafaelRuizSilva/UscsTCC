from fastapi import APIRouter, Depends, HTTPException, Query, Path
from app.core.models.projeto import Projeto
from app.adapters.repositories.projeto_repository import ProjetoRepository
from app.core.use_cases.create_projeto_usecase import CreateProjetoUseCase
from app.core.use_cases.deletar_projeto_usecase import DeletarProjetoUseCase
from app.dependencies import get_db_conn
from app.adapters.repositories.atualiza_aluno_projeto_repository import ProjetoGateway
from app.core.security import get_current_user
from app.core.models.upd_aluno_projeto_model import UpdateProjetoAlunosDTO
from app.core.use_cases.atualizar_alunos_projeto import UpdateProjetoAlunosUseCase
from app.core.use_cases.listar_projetos_por_orientador_usecase import ListarProjetosPorOrientadorUseCase  # ✅


router = APIRouter(prefix="/projetos", tags=["Projetos"])

@router.get("/me")
def get_meus_projetos(
    db=Depends(get_db_conn),
    orientador_id: int = Depends(get_current_user("orientador")),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """
    Lista projetos do orientador autenticado (paginável).
    Retorna {"projetos": [...]} no mesmo shape do get_all().
    """
    repo = ProjetoRepository(db)
    usecase = ListarProjetosPorOrientadorUseCase(repo)
    projetos = usecase.execute(orientador_id, limit=limit, offset=offset)
    return {"projetos": projetos}

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


@router.delete("/{id_projeto}")
def deletar_projeto(id_projeto: int, db=Depends(get_db_conn)):
    repo = ProjetoRepository(db)
    use_case = DeletarProjetoUseCase(repo)

    try:
        use_case.execute(id_projeto)
        return {"success": True, "message": f"Projeto {id_projeto} deletado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Erro ao deletar projeto")

@router.post("/update-alunos")
def update_alunos_projeto(
    dto: UpdateProjetoAlunosDTO,
    db=Depends(get_db_conn),
    orientador_id: int = Depends(get_current_user("orientador"))
):
    try:
        gateway = ProjetoGateway(db)
        usecase = UpdateProjetoAlunosUseCase(gateway)
        usecase.execute(dto)
        return {"mensagem": "Alunos atualizados com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/")
def get_projetos(db=Depends(get_db_conn)):
    repo = ProjetoRepository(db)
    projetos = repo.get_all()
    return {"projetos": projetos}

@router.get("/{id_projeto}/alunos")
def listar_alunos_do_projeto(
    id_projeto: int = Path(..., ge=1),
    db=Depends(get_db_conn),
):
    """
    Retorna todos os alunos vinculados ao projeto informado.
    Sem necessidade de autenticação.
    """
    try:
        repo = ProjetoRepository(db)
        alunos = repo.listar_alunos_por_projeto(id_projeto)
        return {"id_projeto": id_projeto, "alunos": alunos}  # [] se não houver vínculos
    except Exception:
        raise HTTPException(status_code=500, detail="Erro inesperado ao listar alunos do projeto")

