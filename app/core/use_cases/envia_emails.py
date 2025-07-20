import pandas as pd
from app.core.ports.input.porta_envia_emails import PortaEnviaEmail
from app.core.models.destinatario import Destinatario

class EnviaEmailUseCase(PortaEnviaEmail):
    def __init__(self, email_sender):
        self.email_sender = email_sender

    def execute(self, file):
        qtd_emails_enviados = 0
        df = pd.read_excel(file.file)
        for _, row in df.iterrows():
            destinatario = Destinatario(name=row['nome'], email=row['email'],
                                        data_conclusao=row['data_conclusao'],
                                        cpf=row['cpf'], ciclo=row['ciclo'])
            self.email_sender.send_email(destinatario)
            qtd_emails_enviados += 1

        return qtd_emails_enviados