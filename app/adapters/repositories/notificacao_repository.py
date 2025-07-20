from app.core.models.notificacao import Notificacao
from app.core.ports.output.porta_notificacao_repository import INotificacaoRepository

class NotificacaoRepository(INotificacaoRepository):
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def salvar(self, notificacao: Notificacao) -> int:
        cursor = self.db_conn.cursor()
        query = """
        INSERT INTO tb_notificacao (tipo, mensagem, destinatario, lida, data_criacao)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            notificacao.tipo,
            notificacao.mensagem,
            notificacao.destinatario,
            notificacao.lida,
            notificacao.data_criacao
        ))

        self.db_conn.commit()
        return cursor.lastrowid