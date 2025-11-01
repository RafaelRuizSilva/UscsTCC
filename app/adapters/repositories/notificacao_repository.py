from app.core.models.notificacao import Notificacao
from app.core.ports.output.porta_notificacao_repository import INotificacaoRepository

# helper: tenta abrir cursor dict; se não der, usa cursor normal
def _dict_cursor(conn):
    try:
        import pymysql  # PyMySQL
        return conn.cursor(pymysql.cursors.DictCursor)
    except Exception:
        # fallback: cursor padrão (tuplas)
        return conn.cursor()

# helper: extrai "total" de COUNT(*)
def _read_total(row):
    if row is None:
        return 0
    if isinstance(row, dict):
        # tenta chaves comuns de count
        for k in ("total", "count", "COUNT(*)"):
            if k in row:
                return row[k] or 0
        # se veio com alias diferente, pega o primeiro valor
        return next(iter(row.values())) or 0
    # tupla
    return row[0] or 0

# helper: converte lista de tuplas -> lista de dicts usando cursor.description
def _rows_to_dicts(rows, cursor):
    if not rows:
        return []
    if isinstance(rows[0], dict):
        return rows
    cols = [d[0] for d in cursor.description]  # nomes das colunas
    return [dict(zip(cols, r)) for r in rows]

class NotificacaoRepository(INotificacaoRepository):
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def salvar(self, notificacao: Notificacao) -> int:
        with self.db_conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tb_notificacao (tipo, mensagem, destinatario, lida, data_criacao)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    notificacao.tipo,
                    notificacao.mensagem,
                    notificacao.destinatario,
                    notificacao.lida,
                    notificacao.data_criacao,
                ),
            )
            self.db_conn.commit()
            return cursor.lastrowid

    def listar_por_destinatario(self, destinatario: str, page: int, size: int):
        offset = (page - 1) * size

        # COUNT
        with _dict_cursor(self.db_conn) as c1:
            c1.execute(
                "SELECT COUNT(*) AS total FROM tb_notificacao WHERE destinatario=%s",
                (destinatario,),
            )
            row = c1.fetchone()
            total = _read_total(row)

        # PAGE
        with self.db_conn.cursor() as c2:
            c2.execute(
                """
                SELECT id, tipo, mensagem, destinatario, lida, data_criacao
                FROM tb_notificacao
                WHERE destinatario=%s
                ORDER BY data_criacao DESC
                LIMIT %s OFFSET %s
                """,
                (destinatario, size, offset),
            )
            items = c2.fetchall()
            items = _rows_to_dicts(items, c2)

        return items, total

    def marcar_todas_lidas(self, destinatario: str) -> int:
        with self.db_conn.cursor() as cursor:
            cursor.execute(
                "UPDATE tb_notificacao SET lida=1 WHERE destinatario=%s AND lida=0",
                (destinatario,),
            )
            self.db_conn.commit()
            return cursor.rowcount
