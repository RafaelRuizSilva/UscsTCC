from datetime import datetime
from pydantic import BaseModel, Field

class Notificacao(BaseModel):
    id: int | None = None
    tipo: str
    mensagem: str
    destinatario: str  # Ex: "secretaria", "aluno", etc.
    lida: bool = False
    data_criacao: datetime = Field(default_factory=datetime.now())

class NotificacaoCreate(BaseModel):
    tipo: str
    mensagem: str
    destinatario: str
