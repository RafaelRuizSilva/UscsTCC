from pydantic import BaseModel
from typing import List

class UpdateProjetoAlunosDTO(BaseModel):
    id_projeto: int
    id_alunos: List[int]
