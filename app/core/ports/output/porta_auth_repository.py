from abc import ABC, abstractmethod
from typing import Optional, Dict

class IAuthRepository(ABC):
    @abstractmethod
    def find_account_by_email(self, email: str) -> Optional[Dict]:
        """
        Retorna dict: {"id": int, "email": str, "nome_completo": str|None, "user_type": 'aluno'|'orientador'|'secretaria'}
        ou None se não encontrar.
        """
        ...

    @abstractmethod
    def update_password_hash(self, user_type: str, user_id: int, senha_hash: str) -> None:
        """Atualiza a senha do usuário informado."""
        ...
