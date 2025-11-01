from pydantic import BaseModel, Field, field_validator

class UpdateProjetoAlunosDTO(BaseModel):
    id_projeto: int = Field(..., gt=0)
    id_alunos: list[int] = Field()

    @field_validator("id_alunos")
    @classmethod
    def valida_ids(cls, v: list[int]):
        return [int(x) for x in v if int(x) > 0]
