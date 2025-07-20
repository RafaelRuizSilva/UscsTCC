# core/ports/output/porta_notificacao_repository.py
"""Saída (output port) para notificações.
Define as operações que o domínio precisa do adaptador de persistência.
"""
from abc import ABC, abstractmethod
from app.core.models.notificacao import Notificacao


class INotificacaoRepository(ABC):
    """Interface que descreve o contrato para salvar e consultar notificações."""

    # ✔️ CREATE ------------------------------------------------------
    @abstractmethod
    def salvar(self, notificacao: Notificacao) -> int:
        """Cria a notificação e retorna o ID gerado."""
        pass

