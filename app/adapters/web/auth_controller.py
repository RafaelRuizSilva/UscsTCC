from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import verificar_senha, criar_token_acesso, criar_token_refresh, verificar_token
from app.dependencies.db import get_db_conn
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.models.auth_reset import ForgotPasswordRequest, ResetPasswordRequest
from app.adapters.repositories.auth_repository import AuthRepository
from app.adapters.repositories.password_reset_token_repository import PasswordResetTokenRepository
from app.adapters.email.smtp_email_sender_reset_password import SmtpEmailSender
from app.core.use_cases.request_password_reset_usecase import RequestPasswordResetUseCase
from app.core.use_cases.reset_password_usecase import ResetPasswordUseCase
from datetime import datetime

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db_conn)):
    email = form_data.username
    senha = form_data.password

    cur = db.cursor()
    cur.execute("""
        SELECT id_aluno, senha_hash, status, inadimplente_ate
          FROM tb_cadastro_aluno
         WHERE email=%s
         LIMIT 1
    """, (email,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    aluno_id, senha_hash, status_atual, inad_ate = row

    if not verificar_senha(senha, senha_hash):
        raise HTTPException(status_code=401, detail="Senha incorreta")

    status_atual = (status_atual or "").upper()

    # 🔴 PRIORIDADE 1 — INADIMPLENTE
    if status_atual == "INADIMPLENTE":
        raise HTTPException(status_code=403, detail="Usuário inadimplente no momento.")

    # 🔴 PRIORIDADE 2 — REPROVADO
    if status_atual == "REPROVADO":
        raise HTTPException(status_code=403, detail="Cadastro reprovado pela Secretaria.")

    # 🔴 PRIORIDADE 3 — NÃO APROVADO
    if status_atual != "APROVADO":
        raise HTTPException(status_code=403, detail="Cadastro pendente de aprovação da Secretaria.")

    access_token  = criar_token_acesso({"sub": str(aluno_id), "role": "aluno"})
    refresh_token = criar_token_refresh({"sub": str(aluno_id), "role": "aluno"})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/login-orientador")
def login_orientador(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db_conn)):
    email = form_data.username
    senha = form_data.password

    cur = db.cursor()
    cur.execute("""
        SELECT id_orientador, senha_hash, status, inadimplente_ate
          FROM tb_cadastro_orientador
         WHERE email=%s
         LIMIT 1
    """, (email,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    orientador_id, senha_hash, status_atual, inad_ate = row

    if not verificar_senha(senha, senha_hash):
        raise HTTPException(status_code=401, detail="Senha incorreta")

    status_atual = (status_atual or "").upper()

    # 🔴 PRIORIDADE 1 — INADIMPLENTE
    if status_atual == "INADIMPLENTE":
        raise HTTPException(status_code=403, detail="Usuário inadimplente no momento.")

    # 🔴 PRIORIDADE 2 — REPROVADO
    if status_atual == "REPROVADO":
        raise HTTPException(status_code=403, detail="Cadastro reprovado pela Secretaria.")

    # 🔴 PRIORIDADE 3 — NÃO APROVADO
    if status_atual != "APROVADO":
        raise HTTPException(status_code=403, detail="Cadastro pendente de aprovação da Secretaria.")

    access_token  = criar_token_acesso({"sub": str(orientador_id), "role": "orientador"})
    refresh_token = criar_token_refresh({"sub": str(orientador_id), "role": "orientador"})

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
        role = payload.get("role")  # 👈 preserve a role
        if not user_id or not role:
            raise HTTPException(status_code=401, detail="Refresh token inválido")
        novo_access = criar_token_acesso({"sub": str(user_id), "role": role})
        return {"access_token": novo_access, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

# ---------- SOLICITAR REDEFINIÇÃO ----------
@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(body: ForgotPasswordRequest, db=Depends(get_db_conn)):
    auth_repo = AuthRepository(db)
    token_repo = PasswordResetTokenRepository(db)
    email_sender = SmtpEmailSender()  # usa suas mesmas credenciais

    uc = RequestPasswordResetUseCase(
        auth_repo=auth_repo,
        token_repo=token_repo,
        email_sender=email_sender,
        ttl_minutes=60,
        reset_link_base='http://ic.inovauscs.tech/reset-password'  
    )
    uc.execute(body.email)
    return {"message": "Se o e-mail existir, enviaremos instruções para redefinição."}

# ---------- EFETIVAR REDEFINIÇÃO ----------
@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    body: ResetPasswordRequest,
    db=Depends(get_db_conn),
):
    token_repo = PasswordResetTokenRepository(db)
    auth_repo = AuthRepository(db)
    uc = ResetPasswordUseCase(token_repo=token_repo, auth_repo=auth_repo)
    try:
        uc.execute(token=body.token, nova_senha=body.nova_senha)
        return {"message": "Senha redefinida com sucesso."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Erro inesperado ao redefinir senha.")


