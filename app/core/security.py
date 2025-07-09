from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from app.configs import settings  # pegar SECRET_KEY do settings
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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

def get_current_user(role_esperado: str):
    def _dependency(token: str = Depends(oauth2_scheme)):
        try:
            payload = verificar_token(token)
            role = payload.get("role")
            user_id = payload.get("sub")

            if role != role_esperado:
                raise HTTPException(status_code=403, detail="Acesso negado ao tipo de usuário")

            return user_id  # ou return payload se quiser o pacote completo

        except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e))

    return _dependency