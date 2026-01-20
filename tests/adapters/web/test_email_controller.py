import io
import pandas as pd
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)

@patch("app.adapters.web.email_controller.EnviaEmailUseCase")
def test_send_emails_excel_success(mock_use_case_class):
    # Arrange
    df = pd.DataFrame({
        "nome": ["Rafael"],
        "email": ["rafael@gmail.com"],
        "cpf": ["123.456.789-00"],
        "data_conclusao": ["2024-06-30"],
        "ciclo": ["2023-2024"]
    })

    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)

    use_case_mock = MagicMock()
    use_case_mock.execute.return_value = 1
    mock_use_case_class.return_value = use_case_mock

    # Act
    response = client.post(
        "/send-emails",
        files={"file": ("emails.xlsx", excel_buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["quantidade_enviada"] == 1
    mock_use_case_class.assert_called_once()

def test_send_emails_arquivo_nao_excel():
    file = io.BytesIO(b"dummy content")
    response = client.post(
        "/send-emails",
        files={"file": ("teste.txt", file, "text/plain")}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == 'Formato de arquivo inválido. Envie um arquivo excel (.xlsx).'

@patch("app.adapters.web.email_controller.EnviaEmailUseCase")
def test_send_emails_internal_server_error(mock_use_case_class):
    mock_file = io.BytesIO(b"dummy excel content")
    mock_use_case = MagicMock()
    mock_use_case.execute.side_effect = Exception("erro simulado")
    mock_use_case_class.return_value = mock_use_case

    response = client.post(
        "/send-emails",
        files={"file": ("teste.xlsx", mock_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )

    assert response.status_code == 500
    assert "Erro interno" in response.json()["detail"]
