from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.db import get_db_conn
from app.core.security import get_current_user
from app.adapters.repositories.secretaria_repository import SecretariaRepository
from app.core.ports.output.porta_secretaria_repository import ISecretariaRepository
from app.core.models.secretaria import Secretaria
from app.core.models.secretaria_login import SecretariaLogin
from app.core.use_cases.create_secretaria_usecase import CreateSecretariaUseCase
from app.core.use_cases.login_secretaria_usecase import LoginSecretariaUseCase

router = APIRouter(prefix="/secretarias", tags=["Secretarias"])

# DI mínima do repo
def get_repo(db=Depends(get_db_conn)) -> ISecretariaRepository:
    return SecretariaRepository(db)

# -------- CADASTRAR (somente secretária logada pode criar) --------
@router.post("/", status_code=status.HTTP_201_CREATED)
def cadastrar_secretaria(
    secretaria: Secretaria,
    _user_id: int = Depends(get_current_user("secretaria")),  # protege a rota
    repo: Annotated[ISecretariaRepository, Depends(get_repo)] = None,
):
    usecase = CreateSecretariaUseCase(repo)
    try:
        nova_id = usecase.execute(secretaria)
        return {"id": nova_id, "mensagem": "Secretaria cadastrada com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro inesperado")

# -------------------- LOGIN --------------------
@router.post("/login", status_code=status.HTTP_200_OK)
def login_secretaria(
    credenciais: SecretariaLogin,
    repo: Annotated[ISecretariaRepository, Depends(get_repo)],
):
    uc = LoginSecretariaUseCase(repo)
    try:
        token_data = uc.execute(credenciais.email, credenciais.senha)
        return token_data  # {"access_token": "...", "token_type": "bearer"}
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao autenticar")

# Rota de verificação (opcional)
@router.get("/painel-secretaria")
def painel_secretaria(user_id: int = Depends(get_current_user("secretaria"))):
    return {"msg": f"Secretaria autenticada: ID {user_id}"}
