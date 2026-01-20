from datetime import date
from app.core.models.destinatario import Destinatario

def test_cria_destinatario():
    r = Destinatario("Rafael",
                     "rafael@gmail.com",
                     "123.456.789-00",
                     date(2024, 6, 30),
                     "2023-2024")

    assert r.name == "Rafael"
    assert r.data_conclusao.year == 2024
    assert r.cpf == "123.456.789-00"
    assert r.ciclo == "2023-2024"
    assert isinstance(r.data_conclusao, date)
