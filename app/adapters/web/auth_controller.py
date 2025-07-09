from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import verificar_senha, criar_token_acesso, criar_token_refresh, verificar_token
from app.dependencies.db import get_db_conn
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

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

    access_token = criar_token_acesso({"sub": str(aluno_id), "role": "aluno"})
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

    orientador_id, senha_hash = result

    if not verificar_senha(senha, senha_hash):
        raise HTTPException(status_code=401, detail="Senha incorreta")

    access_token = criar_token_acesso({"sub": str(orientador_id), "role": "orientador"})
    refresh_token = criar_token_refresh({"sub": str(orientador_id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

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

