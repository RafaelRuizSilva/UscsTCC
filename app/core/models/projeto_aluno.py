from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ProjetoAluno:
    id_projeto: int
    id_aluno: int
    status_aluno: bool
    created_at: Optional[datetime] = None
