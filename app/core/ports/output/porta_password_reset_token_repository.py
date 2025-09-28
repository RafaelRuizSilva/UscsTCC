from abc import ABC, abstractmethod
from typing import Optional, Dict
from datetime import datetime

class IPasswordResetTokenRepository(ABC):
    @abstractmethod
    def create_token(self, user_type: str, user_id: int, token_hash: str, expires_at: datetime) -> int:
        ...

    @abstractmethod
    def get_valid_by_hash(self, token_hash: str) -> Optional[Dict]:
        """
        Retorna dict: {"id": int, "user_type": str, "user_id": int, "expires_at": datetime, "used_at": datetime|None}
        Somente se existir (sem checar expiração/used aqui, pode checar no use case).
        """
        ...

    @abstractmethod
    def mark_used(self, token_id: int) -> None:
        ...
