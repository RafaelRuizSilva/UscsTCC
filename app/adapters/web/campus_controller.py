from fastapi import APIRouter, Depends, HTTPException
from app.core.models.campus import Campus
from app.adapters.repositories.campus_repository import CampusRepository
from app.core.use_cases.create_campus_repository import CreateCampusUseCase
from app.dependencies.db import get_db_conn
from app.core.use_cases.get_campus_by_id_usecase import GetCampusByIdUseCase
from app.core.use_cases.update_campus_usecase import UpdateCampusUseCase
from app.core.use_cases.del_campus_usecase import DeleteCampusUseCase
from app.core.security import get_current_user

router = APIRouter(prefix="/campus", tags=["Campus"])


@router.post("/")
def cadastrar_campus(
    campus: Campus,
    db=Depends(get_db_conn),
    id_secretaria: int = Depends(get_current_user("secretaria"))
):
    repo = CampusRepository(db)
    usecase = CreateCampusUseCase(repo)
    try:
        campus_id = usecase.execute(campus)
        return {"id": campus_id, "mensagem": "Campus cadastrado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao cadastrar campus: {e}"
        )


@router.get("/")
def get_campus(db=Depends(get_db_conn),
               ):
    repo = CampusRepository(db)
    try:
        campus = repo.get_all()
        return {"campus": campus}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar campus: {e}"
        )


@router.get("/{campus_id}", response_model=Campus)
def get_campus_by_id(campus_id: int, db=Depends(get_db_conn)):
    repo = CampusRepository(db)
    usecase = GetCampusByIdUseCase(repo)
    try:
        campus = usecase.execute(campus_id)
        if not campus:
            raise HTTPException(status_code=404, detail="Campus não encontrado")
        return campus
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar campus: {e}"
        )


@router.put("/{campus_id}", status_code=200)
def update_campus(
    campus_id: int,
    campus: Campus,
    db=Depends(get_db_conn),
    id_secretaria: int = Depends(get_current_user("secretaria"))
):
    repo = CampusRepository(db)
    usecase = UpdateCampusUseCase(repo)
    try:
        usecase.execute(campus_id, campus)
        return {"mensagem": "Campus atualizado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar campus: {e}"
        )


@router.delete("/{campus_id}", status_code=204)
def delete_campus(
    campus_id: int,
    db=Depends(get_db_conn),
    id_secretaria: int = Depends(get_current_user("secretaria"))
):
    repo = CampusRepository(db)
    usecase = DeleteCampusUseCase(repo)
    try:
        usecase.execute(campus_id)
        return {"mensagem": "Campus excluído com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao excluir campus: {e}"
        )
