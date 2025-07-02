from pydantic import BaseModel, Field


class Projeto(BaseModel):
    titulo_projeto: str = Field(..., min_length=1, max_length=255)
    resumo: str = Field(..., max_length=1000)
    id_orientador: int
    id_campus: int