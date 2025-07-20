from fastapi import APIRouter, Depends
from app.core.models.campus import Campus
from app.adapters.repositories.campus_repository import CampusRepository
from app.core.use_cases.create_campus_repository import CreateCampusUseCase
from app.dependencies import get_db_conn

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