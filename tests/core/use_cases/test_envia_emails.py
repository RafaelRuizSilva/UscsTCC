import io
import pandas as pd
from unittest.mock import MagicMock
from app.core.use_cases.envia_emails import EnviaEmailUseCase

def test_send_emails_from_excel(mocker):
    # 1. Criar DataFrame com os dados simulados
    df = pd.DataFrame({
        "nome": ["Rafael"],
        "email": ["rafael@email.com"],
        "cpf": ["123.456.789-00"],
        "data_conclusao": ["2024-06-30"],
        "ciclo": ["2023-2024"]
    })

    # 2. Salvar esse DataFrame em memória como arquivo Excel
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)

    # 3. Mockar o arquivo que seria recebido pela API
    mock_file = mocker.MagicMock()
    mock_file.filename = "teste.xlsx"
    mock_file.file = excel_buffer  # Simula o .file do UploadFile

    # 4. Criar sender mock e executar use case
    sender_mock = MagicMock()
    use_case = EnviaEmailUseCase(email_sender=sender_mock)
    quantidade = use_case.execute(mock_file)

    # 5. Verificações
    assert quantidade == 1
    sender_mock.send_email.assert_called_once()
