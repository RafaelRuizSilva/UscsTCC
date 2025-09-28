import hashlib
from datetime import datetime, timezone
from app.core.ports.output.porta_password_reset_token_repository import IPasswordResetTokenRepository
from app.core.ports.output.porta_auth_repository import IAuthRepository
from app.core.security import gerar_hash_senha


class ResetPasswordUseCase:
    def __init__(self, token_repo: IPasswordResetTokenRepository, auth_repo: IAuthRepository):
        self.token_repo = token_repo
        self.auth_repo = auth_repo

    def execute(self, token: str, nova_senha: str) -> None:
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        rec = self.token_repo.get_valid_by_hash(token_hash)
        if not rec:
            raise ValueError("Token inválido")

        # valida expiração/uso
        now = datetime.now(timezone.utc)
        expires_at = rec["expires_at"]
        if expires_at.tzinfo is None:
            # se vier naive do driver, considere UTC
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if rec.get("used_at"):
            raise ValueError("Token já utilizado")
        if now > expires_at:
            raise ValueError("Token expirado")

        # atualiza senha
        senha_hash = gerar_hash_senha(nova_senha)
        self.auth_repo.update_password_hash(rec["user_type"], rec["user_id"], senha_hash)

        # marca token como usado
        self.token_repo.mark_used(rec["id"])
