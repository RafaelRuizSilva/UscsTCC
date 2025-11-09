from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from app.core.models.orientador import Orientador
from app.core.models.orientador_out import OrientadorOut
from app.adapters.repositories.orientador_repository import OrientadorRepository
from app.core.use_cases.create_orientador_usecase import CreateOrientadorUseCase
from app.core.use_cases.listar_todos_orientadores_usecase import ListarTodosOrientadoresUseCase
from app.core.use_cases.obter_orientador_por_id_usecase import ObterOrientadorPorIdUseCase
from app.core.use_cases.obter_orientador_por_nome_usecase import ObterOrientadorPorNomeUseCase
from app.dependencies.db import get_db_conn
from app.core.security import get_current_user
from app.core.use_cases.aprovar_orientador_usecase import AprovarOrientadorUseCase
from app.core.use_cases.reprovar_orientador_usecase import ReprovarOrientadorUseCase
from typing import Annotated
from app.core.ports.output.porta_projeto_repository import IProjetoRepository
from app.adapters.repositories.projeto_repository import ProjetoRepository
from app.core.ports.output.porta_orientador_repository import IOrientadorRepository
from app.core.use_cases.inadimplentar_orientador_projeto_usecase import InadimplentarOrientadorDoProjetoUseCase

router = APIRouter(prefix="/orientadores", tags=["Orientadores"])

def get_projeto_repo(db=Depends(get_db_conn)) -> IProjetoRepository:
    return ProjetoRepository(db)

def get_orientador_repo(db=Depends(get_db_conn)) -> IOrientadorRepository:
    return OrientadorRepository(db)

@router.post("/{id_projeto}/inadimplentar-orientador", status_code=status.HTTP_200_OK)
def inadimplentar_orientador_do_projeto(
    id_projeto: int = Path(..., ge=1),
    projeto_repo: Annotated[IProjetoRepository, Depends(get_projeto_repo)] = None,
    orientador_repo: Annotated[IOrientadorRepository, Depends(get_orientador_repo)] = None,
):
    try:
        id_orientador = InadimplentarOrientadorDoProjetoUseCase(projeto_repo, orientador_repo).execute(id_projeto)
        return {
            "mensagem": "Orientador reprovado e marcado como inadimplente por 2 anos.",
            "id_orientador": id_orientador
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao inadimplentar orientador do projeto: {e}")

@router.post("/")
def cadastrar_orientador(orientador: Orientador, db=Depends(get_db_conn)):
    repo = OrientadorRepository(db)
    usecase = CreateOrientadorUseCase(repo)
    try:
        orientador_id = usecase.execute(orientador)
        return {"id": orientador_id, "mensagem": "Orientador cadastrado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {e}")

@router.get("/painel-orientador")
def painel(user_id: int = Depends(get_current_user("orientador"))):
    return {"msg": f"Orientador autenticado: ID {user_id}"}

@router.get("/", response_model=List[OrientadorOut])
def listar_todos_orientadores(db=Depends(get_db_conn)):
    repo = OrientadorRepository(db)
    usecase = ListarTodosOrientadoresUseCase(repo)
    return usecase.execute()

@router.get("/buscar", response_model=OrientadorOut)
def obter_orientador_por_nome(nome: str = Query(..., min_length=1), db=Depends(get_db_conn)):
    repo = OrientadorRepository(db)
    usecase = ObterOrientadorPorNomeUseCase(repo)
    result = usecase.execute(nome)
    if not result:
        raise HTTPException(status_code=404, detail="Orientador não encontrado pelo nome informado")
    return result

@router.get("/aprovados")
def listar_aprovados(db=Depends(get_db_conn)):
    repo = OrientadorRepository(db)
    return repo.listar_aprovados()

@router.get("/inadimplentes", status_code=status.HTTP_200_OK)
def listar_inadimplentes(db=Depends(get_db_conn)):
    repo = OrientadorRepository(db)
    return {"orientadores": repo.list_inadimplentes()}

@router.get("/{id}", response_model=OrientadorOut)
def obter_orientador_por_id(id: int = Path(..., ge=1), db=Depends(get_db_conn)):
    repo = OrientadorRepository(db)
    usecase = ObterOrientadorPorIdUseCase(repo)
    result = usecase.execute(id)
    if not result:
        raise HTTPException(status_code=404, detail="Orientador não encontrado")
    return result

@router.put("/{id}/aprovar", status_code=status.HTTP_200_OK)
def aprovar_orientador(id: int, db=Depends(get_db_conn)):
    repo = OrientadorRepository(db)
    try:
        AprovarOrientadorUseCase(repo).execute(id)
        return {"mensagem": "Orientador aprovado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao aprovar orientador: {e}")

@router.put("/{id}/status", status_code=status.HTTP_200_OK)
def atualizar_status_orientador(
    id: int,
    novo_status: str,
    db=Depends(get_db_conn)
):
    repo = OrientadorRepository(db)
    try:
        # Chama o métod update_status do repositório para atualizar o status do orientador
        repo.update_status(id, novo_status)
        return {"mensagem": "Status do orientador atualizado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))  # Orientador não encontrado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar status do orientador: {e}")

@router.put("/{id}/reprovar", status_code=status.HTTP_200_OK)
def reprovar_orientador(id: int, db=Depends(get_db_conn)):
    repo = OrientadorRepository(db)
    try:
        ReprovarOrientadorUseCase(repo).execute(id)
        return {"mensagem": "Orientador reprovado e marcado como inadimplente por 2 anos"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao reprovar orientador: {e}")
