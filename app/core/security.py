from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from app.configs import settings  # pegar SECRET_KEY do settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Union, List
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

SECRET_KEY = settings.SECRET_KEY  # ✅ uso correto da chave via config centralizada

def gerar_hash_senha(senha):
    return pwd_context.hash(senha)

def verificar_senha(senha, senha_hash):
    return pwd_context.verify(senha, senha_hash)

def criar_token_acesso(dados: dict):
    dados_exp = dados.copy()
    expira = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    dados_exp.update({"exp": expira})
    return jwt.encode(dados_exp, SECRET_KEY, algorithm=ALGORITHM)

def criar_token_refresh(dados: dict):
    dados_exp = dados.copy()
    expira = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    dados_exp.update({"exp": expira})
    return jwt.encode(dados_exp, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expirado")
    except jwt.PyJWTError:
        raise ValueError("Token inválido")

def get_current_user(roles_esperados: Union[str, List[str]]):
    if isinstance(roles_esperados, str):
        roles_esperados = [roles_esperados]

    def _dependency(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token não informado",
            )

        token = credentials.credentials

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado",
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )

        role = payload.get("role")
        user_id = payload.get("sub")

        if role not in roles_esperados:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado",
            )

        return user_id

    return _dependency