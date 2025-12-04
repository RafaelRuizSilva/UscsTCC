from fastapi import APIRouter, Depends, HTTPException
from app.core.models.curso import Curso
from app.adapters.repositories.curso_repository import CursoRepository
from app.core.use_cases.create_curso_usecase import CreateCursoUseCase
from app.core.use_cases.get_curso_by_id_usecase import GetCursoByIdUseCase
from app.core.use_cases.upd_curso_usecase import UpdateCursoUseCase
from app.core.use_cases.del_curso_usecase import DeleteCursoUseCase
from app.dependencies.db import get_db_conn
from app.core.security import get_current_user

router = APIRouter(prefix="/cursos", tags=["Cursos"])

@router.post("/")
def cadastrar_curso(curso: Curso, db=Depends(get_db_conn),
                    id_secretaria: int = Depends(get_current_user("secretaria")),
                    ):
   repo = CursoRepository(db)
   usecase = CreateCursoUseCase(repo)
   curso_id = usecase.execute(curso)
   return {"id": curso_id, "mensagem": "Curso cadastrado com sucesso"}

@router.get("/")
def get_cursos(db=Depends(get_db_conn)):
    repo = CursoRepository(db)
    cursos = repo.get_all()
    return {"cursos": cursos}

@router.get("/{curso_id}", response_model=Curso)
def get_curso_by_id(curso_id: int, db=Depends(get_db_conn)):
    repo = CursoRepository(db)
    usecase = GetCursoByIdUseCase(repo)
    curso = usecase.execute(curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    return curso

@router.put("/{curso_id}", status_code=200)
def update_curso(curso_id: int, curso: Curso, db=Depends(get_db_conn),
                 id_secretaria: int = Depends(get_current_user("secretaria"))):
    repo = CursoRepository(db)
    usecase = UpdateCursoUseCase(repo)
    try:
        usecase.execute(curso_id, curso)
        return {"mensagem": "Curso atualizado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar curso: {e}")

@router.delete("/{curso_id}", status_code=204)
def delete_curso(curso_id: int, db=Depends(get_db_conn),
                 id_secretaria: int = Depends(get_current_user("secretaria"))):
    repo = CursoRepository(db)
    usecase = DeleteCursoUseCase(repo)
    try:
        usecase.execute(curso_id)
        return {"mensagem": "Curso excluído com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir curso: {e}")
