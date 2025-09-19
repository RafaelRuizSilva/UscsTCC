from app.core.security import get_current_user
from app.core.use_cases.create_inscricao_usecase import CriarInscricaoUseCase
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.models.inscricao import InscricaoCreate
from app.core.use_cases.list_inscricoes_usecase import ListarInscricoesUseCase
from app.core.use_cases.get_inscricao_usecase import ObterInscricaoPorIdUseCase
from app.core.use_cases.delete_inscricao_usecase import ExcluirInscricaoUseCase
from app.adapters.repositories.inscricao_repository import InscricaoRepository
from app.core.ports.output.porta_inscricao_repository import IInscricaoRepository
from app.dependencies.db import get_db_conn
from typing import Annotated

router = APIRouter(prefix="/inscricao", tags=['Inscrição'])

def get_repo(db=Depends(get_db_conn)) -> IInscricaoRepository:
    return InscricaoRepository(db)

# -------------------- GET ALL --------------------
@router.get("/", status_code=status.HTTP_200_OK)
def listar_inscricoes(
    repo: IInscricaoRepository = Depends(get_repo)
):
    use_case = ListarInscricoesUseCase(repo)
    try:
        return use_case.execute()
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno ao listar inscrições. {ex}")

# -------------------- GET BY ID --------------------
@router.get("/{id_inscricao}", status_code=status.HTTP_200_OK)
def obter_inscricao_por_id(
    id_inscricao: int,
    repo: IInscricaoRepository = Depends(get_repo)
):
    use_case = ObterInscricaoPorIdUseCase(repo)
    try:
        data = use_case.execute(id_inscricao)
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscrição não encontrada.")
        return data
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao obter inscrição.")

# -------------------- DELETE BY ID --------------------
@router.delete("/{id_inscricao}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_inscricao(
    id_inscricao: int,
    repo: IInscricaoRepository = Depends(get_repo)
):
    use_case = ExcluirInscricaoUseCase(repo)
    try:
        use_case.execute(id_inscricao)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao excluir inscrição.")


@router.post("/inscrever", status_code=status.HTTP_201_CREATED)
def inscrever_aluno(
    inscricao: InscricaoCreate,
    repo: Annotated[IInscricaoRepository, Depends(get_repo)],  # Injeção do repo aqui
    id_aluno: int = Depends(get_current_user("aluno"))  # Autenticação do aluno
):
    """
    Endpoint para inscrever um aluno em um projeto.
    Recebe o ID do projeto e inscreve o aluno no projeto.
    """
    try:
        # O use case recebe o repositório via dependência
        use_case = CriarInscricaoUseCase(repo)

        # Executa a inscrição
        id_inscricao = use_case.execute(id_aluno, inscricao.id_projeto)

        return {
            "success": True,
            "message": "Inscrição realizada com sucesso!",
            "data": {"id_inscricao": id_inscricao}
        }

    except ValueError as e:
        # Exceção específica para problemas de integridade, como "Aluno já inscrito"
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Exceções genéricas, como erro interno no banco de dados
        raise HTTPException(status_code=500, detail="Erro interno no servidor")