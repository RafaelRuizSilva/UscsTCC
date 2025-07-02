from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import verificar_senha, criar_token_acesso, criar_token_refresh, verificar_token
from app.dependencies.db import get_db_conn
from app.core.security import ALGORITHM, SECRET_KEY
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db_conn)):
    email = form_data.username  # sim, usa 'username' no lugar de 'email'
    senha = form_data.password

    cursor = db.cursor()
    cursor.execute("SELECT id_aluno, senha_hash FROM tb_cadastro_aluno WHERE email = %s", (email,))
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    aluno_id, senha_hash = result

    if not verificar_senha(senha, senha_hash):
        raise HTTPException(status_code=401, detail="Senha incorreta")

    access_token = criar_token_acesso({"sub": str(aluno_id)})
    refresh_token = criar_token_refresh({"sub": str(aluno_id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/login-orientador")
def login_orientador(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db_conn)):
    email = form_data.username  # sim, usa 'username' no lugar de 'email'
    senha = form_data.password

    cursor = db.cursor()
    cursor.execute("SELECT id_orientador, senha_hash FROM tb_cadastro_orientador WHERE email = %s", (email,))
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    aluno_id, senha_hash = result

    if not verificar_senha(senha, senha_hash):
        raise HTTPException(status_code=401, detail="Senha incorreta")

    access_token = criar_token_acesso({"sub": str(aluno_id)})
    refresh_token = criar_token_refresh({"sub": str(aluno_id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = verificar_token(token)
        return payload["sub"]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/refresh-token")
def refresh_token(refresh_token: str):
    try:
        payload = verificar_token(refresh_token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Refresh token inválido")
        novo_access_token = criar_token_acesso({"sub": user_id})
        return {"access_token": novo_access_token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

# --- Exemplo de rota protegida ---
@router.get("/me")
def get_user_logado(user_id: int = Depends(get_current_user)):
    return {"mensagem": f"Você está autenticado como aluno ID {user_id}"}
