from datetime import datetime, date

class Destinatario:
    def __init__(
        self,
        name: str,
        email: str,
        cpf: str,
        data_conclusao,
        ciclo: str
    ):
        self.name = name
        self.email = email
        self.cpf = cpf
        self.ciclo = ciclo

        # ✅ data_conclusao: aceita date ou converte de string
        if isinstance(data_conclusao, date):
            self.data_conclusao = data_conclusao
        else:
            try:
                self.data_conclusao = datetime.strptime(
                    str(data_conclusao),
                    "%d/%m/%Y"
                ).date()
            except ValueError:
                raise ValueError(
                    "data_conclusao deve ser date ou string no formato DD/MM/YYYY"
                )

        self.data_atual = datetime.now().date()
