from typing import Dict
from app.core.ports.output.porta_secretaria_repository import ISecretariaRepository
from app.core.security import verificar_senha, criar_token_acesso  # ajuste o nome se for diferente

class LoginSecretariaUseCase:
    def __init__(self, repo: ISecretariaRepository) -> None:
        self._repo = repo

    def execute(self, email: str, senha: str) -> Dict:
        row = self._repo.get_by_email(email)
        if not row or not verificar_senha(senha, row["senha_hash"]):
            # 401 será tratado no controller
            raise ValueError("Credenciais inválidas")

        # Gera um JWT contendo o id e a role "secretaria"
        token = criar_token_acesso({"sub": str(row["id"]), "role": "secretaria"})
        return {"access_token": token, "token_type": "bearer"}
