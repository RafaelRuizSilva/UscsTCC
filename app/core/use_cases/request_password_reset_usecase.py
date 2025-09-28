import secrets, hashlib
from datetime import datetime, timedelta, timezone
from app.core.ports.output.porta_auth_repository import IAuthRepository
from app.core.ports.output.porta_password_reset_token_repository import IPasswordResetTokenRepository
from app.core.ports.output.porta_email_sender import IEmailSender
from app.configs.settings import TEMPLATE_DIRS
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os


class RequestPasswordResetUseCase:
    def __init__(
        self,
        auth_repo: IAuthRepository,
        token_repo: IPasswordResetTokenRepository,
        email_sender: IEmailSender,
        ttl_minutes: int = 60,
        reset_link_base: str | None = None,  # ex.: "https://app.seusistema.com/reset-senha"
    ):
        self.auth_repo = auth_repo
        self.token_repo = token_repo
        self.email_sender = email_sender
        self.ttl_minutes = ttl_minutes
        self.reset_link_base = reset_link_base  # se None, envia apenas o token

        self.env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIRS),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def execute(self, email: str) -> None:
        # 1) Busca conta; se não existir, retorna silenciosamente (anti user-enumeration)
        acct = self.auth_repo.find_account_by_email(email)
        if not acct:
            return

        # 2) Gera token e salva o HASH (não o token em si)
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=self.ttl_minutes)
        self.token_repo.create_token(acct["user_type"], acct["id"], token_hash, expires_at)

        # 3) Dados base
        nome = (acct.get("nome_completo") or "").strip()
        saudacao_nome = f", {nome}" if nome else ""
        link = f"{self.reset_link_base}?token={token}" if self.reset_link_base else None

        # (a) Texto puro (sempre bom enviar)
        if link:
            text = (
                f"Olá{saudacao_nome}!\n\n"
                "Recebemos uma solicitação para redefinir sua senha.\n"
                f"Acesse o link abaixo (válido por {self.ttl_minutes} minutos):\n{link}\n\n"
                "Se não foi você, ignore este e-mail."
            )
        else:
            text = (
                f"Olá{saudacao_nome}!\n\n"
                f"Seu token de redefinição (válido por {self.ttl_minutes} minutos):\n{token}\n\n"
                "Se não foi você, ignore este e-mail."
            )

        # (b) HTML a partir do template
        try:
            tpl = self.env.get_template("template_email_reset_senha.html")
            html = tpl.render(
                nome=nome or None,  # para o template condicionar a exibição
                link=link,  # se None, ele mostra o bloco de token
                token=token,
                ttl=self.ttl_minutes,
                support_email=os.getenv("SUPPORT_EMAIL", "suporte@uscs.br"),
                year=datetime.now().year,
            )
        except Exception:
            # fallback: sem template, manda só texto
            html = None

        # 4) Envia
        self.email_sender.send(
            to_email=acct["email"],
            subject="Redefinição de senha",
            text=text,
            html=html,
        )