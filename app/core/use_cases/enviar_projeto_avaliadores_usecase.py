from typing import Sequence, Optional
from app.core.ports.output.porta_email_sender import IEmailSender

class EnviarProjetoAvaliadoresUseCase:
    def __init__(self, projeto_repo, email_service: IEmailSender):
        self.projeto_repo = projeto_repo
        self.email = email_service

    def execute(
        self,
        id_projeto: int,
        destinatarios: Sequence[str],
        mensagem: Optional[str],
        assunto: Optional[str],
    ) -> None:
        if not destinatarios or len(destinatarios) > 5:
            raise ValueError("Informe entre 1 e 5 destinatários.")

        meta = self.projeto_repo.get_meta_e_pdf(id_projeto)
        if not meta:
            raise ValueError("Projeto não encontrado.")
        if not meta["pdf"]:
            raise ValueError("Projeto não possui PDF cadastrado.")

        titulo = meta["titulo"]
        pdf_bytes = meta["pdf"]

        subject = assunto or f"USCS • Solicitação de Avaliação — {titulo}"

        # corpo (texto simples)
        text = (
            f"Prezadx avaliador(a),\n\n"
            f"Encaminhamos o projeto \"{titulo}\" para sua avaliação.\n"
            f"Em anexo, o PDF do trabalho.\n\n"
            f"{(mensagem or '').strip()}\n\n"
            f"Atenciosamente,\nUSCS"
        )

        # corpo (HTML no mesmo padrão do reset)
        from html import escape
        mensagem_html = f"<p>{escape(mensagem)}</p>" if mensagem else ""
        html = f"""
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f6f8fb;padding:24px 0;">
          <tr><td align="center">
            <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;font-family:Arial,Helvetica,sans-serif">
              <tr>
                <td style="background:#0b2a4a;height:56px;color:#fff;padding:0 24px;font-size:18px;font-weight:600;border-bottom:4px solid #f59f42;">
                  USCS • Solicitação de Avaliação
                </td>
              </tr>
              <tr>
                <td style="padding:24px; color:#111827; font-size:15px; line-height:1.6;">
                  <p>Olá, avaliador(a) externo(a)!</p>
                  <p>Encaminhamos o projeto <strong>{escape(titulo)}</strong> para sua avaliação.</p>
                  {mensagem_html}
                  <p>O arquivo em PDF segue em anexo a este e-mail.</p>
                  <p>Desde já, agradecemos sua colaboração.</p>
                  <p>Atenciosamente,<br/>USCS</p>
                </td>
              </tr>
              <tr>
                <td style="background:#f9fafb;padding:16px 24px;color:#6b7280;font-size:12px;text-align:center;">
                  Suporte: suporte@uscs.br
                </td>
              </tr>
            </table>
          </td></tr>
        </table>
        """.strip()

        self.email.send_projeto_email(
            to=list(destinatarios),
            subject=subject,
            text=text,
            html=html,
            attachments=[(f"{titulo}.pdf", pdf_bytes, "application/pdf")],
        )

        # Armazenar envio no banco de dados
        self.projeto_repo.salvar_envio_avaliadores(id_projeto, destinatarios)
