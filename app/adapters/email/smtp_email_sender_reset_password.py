import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.ports.output.porta_email_sender import IEmailSender
from app.configs.settings import SMTP_CONFIG

class SmtpEmailSender(IEmailSender):
    def send(self, to_email: str, subject: str, text: str, html: str | None = None) -> None:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SMTP_CONFIG["from"]
        msg["To"] = to_email

        # sempre anexa texto puro
        msg.attach(MIMEText(text, "plain"))
        if html:
            msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(SMTP_CONFIG["host"], SMTP_CONFIG["port"]) as server:
            server.starttls()
            server.login(SMTP_CONFIG["from"], SMTP_CONFIG["password"])  # mesmo padrão do seu remetente
            server.sendmail(SMTP_CONFIG["from"], [to_email], msg.as_string())
