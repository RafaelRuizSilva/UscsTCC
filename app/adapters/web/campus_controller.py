from fastapi import APIRouter, Depends, HTTPException
from app.core.models.campus import Campus
from app.adapters.repositories.campus_repository import CampusRepository
from app.core.use_cases.create_campus_repository import CreateCampusUseCase
from app.dependencies.db import get_db_conn
from app.core.use_cases.get_campus_by_id_usecase import GetCampusByIdUseCase
from app.core.use_cases.update_campus_usecase import UpdateCampusUseCase
from app.core.use_cases.del_campus_usecase import DeleteCampusUseCase

router = APIRouter(prefix="/campus", tags=["Campus"])

@router.post("/")
def cadastrar_campus(campus: Campus, db=Depends(get_db_conn)):
   repo = CampusRepository(db)
   usecase = CreateCampusUseCase(repo)
   campus_id = usecase.execute(campus)
   return {"id": campus_id, "mensagem": "Campus cadastrado com sucesso"}

@router.get("/")
def get_campus(db=Depends(get_db_conn)):
    repo = CampusRepository(db)
    campus = repo.get_all()
    return {"campus": campus}

@router.get("/{campus_id}", response_model=Campus)
def get_campus_by_id(campus_id: int, db=Depends(get_db_conn)):
    repo = CampusRepository(db)
    usecase = GetCampusByIdUseCase(repo)
    campus = usecase.execute(campus_id)
    if not campus:
        raise HTTPException(status_code=404, detail="Campus não encontrado")
    return campus

@router.put("/{campus_id}", status_code=200)
def update_campus(campus_id: int, campus: Campus, db=Depends(get_db_conn)):
    repo = CampusRepository(db)
    usecase = UpdateCampusUseCase(repo)
    try:
        usecase.execute(campus_id, campus)
        return {"mensagem": "Campus atualizado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar campus: {e}")

@router.delete("/{campus_id}", status_code=204)
def delete_campus(campus_id: int, db=Depends(get_db_conn)):
    repo = CampusRepository(db)
    usecase = DeleteCampusUseCase(repo)
    try:
        usecase.execute(campus_id)
        return {"mensagem": "Campus excluído com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir campus: {e}")