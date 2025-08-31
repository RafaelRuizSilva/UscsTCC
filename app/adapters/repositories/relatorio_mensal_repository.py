from typing import List, Optional
from datetime import date
from app.core.models.relatorio_mensal import RelatorioMensalOut, PendenciaOut
from app.core.ports.output.porta_relatorio_mensal_repository import IRelatorioMensalRepository

class RelatorioMensalRepository(IRelatorioMensalRepository):
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def confirmar(self, id_orientador: int, id_projeto: int, mes_ref: date, ok: bool, observacao: Optional[str]) -> int:
        cursor = self.db_conn.cursor()
        try:
            # Garante que o projeto pertence ao orientador autenticado
            cursor.execute(
                "SELECT 1 FROM tb_novo_projeto WHERE id_projeto=%s AND id_orientador=%s LIMIT 1",
                (id_projeto, id_orientador)
            )
            if not cursor.fetchone():
                raise PermissionError("Projeto não pertence ao orientador autenticado.")

            # UPSERT por (id_projeto, mes_referencia)
            query = """
                INSERT INTO tb_relatorio_mensal (id_projeto, id_orientador, mes_referencia, ok, observacao)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                  ok = VALUES(ok),
                  observacao = VALUES(observacao),
                  confirmado_em = CURRENT_TIMESTAMP
            """
            cursor.execute(query, (id_projeto, id_orientador, mes_ref, int(ok), observacao))
            self.db_conn.commit()

            cursor.execute(
                "SELECT id_relatorio FROM tb_relatorio_mensal WHERE id_projeto=%s AND mes_referencia=%s",
                (id_projeto, mes_ref)
            )
            row = cursor.fetchone()
            return int(row[0])
        finally:
            cursor.close()

    def listar_do_orientador_por_mes(self, id_orientador: int, mes_ref: date) -> List[RelatorioMensalOut]:
        cursor = self.db_conn.cursor()
        try:
            query = """
                SELECT id_relatorio, id_projeto, id_orientador, mes_referencia, ok, observacao, confirmado_em
                FROM tb_relatorio_mensal
                WHERE id_orientador = %s AND mes_referencia = %s
                ORDER BY confirmado_em DESC
            """
            cursor.execute(query, (id_orientador, mes_ref))
            rows = cursor.fetchall()
            out: List[RelatorioMensalOut] = []
            for r in rows:
                out.append(RelatorioMensalOut(
                    id_relatorio=r[0],
                    id_projeto=r[1],
                    id_orientador=r[2],
                    mes=r[3].strftime("%Y-%m"),
                    ok=bool(r[4]),
                    observacao=r[5],
                    confirmado_em=r[6]
                ))
            return out
        finally:
            cursor.close()

    def listar_pendentes_do_orientador(self, id_orientador: int, mes_ref: date) -> List[PendenciaOut]:
        cursor = self.db_conn.cursor()
        try:
            query = """
                SELECT p.id_projeto, p.titulo_projeto
                FROM tb_novo_projeto p
                WHERE p.id_orientador = %s
                  AND NOT EXISTS (
                    SELECT 1
                    FROM tb_relatorio_mensal rm
                    WHERE rm.id_projeto = p.id_projeto
                      AND rm.mes_referencia = %s
                  )
                ORDER BY p.id_projeto DESC
            """
            cursor.execute(query, (id_orientador, mes_ref))
            rows = cursor.fetchall()
            return [PendenciaOut(id_projeto=r[0], titulo_projeto=r[1]) for r in rows]
        finally:
            cursor.close()

    def existe_relatorio(self, id_projeto: int, id_orientador: int, mes_ref: date) -> bool:
        cursor = self.db_conn.cursor()
        try:
            cursor.execute("""
                SELECT 1
                FROM tb_relatorio_mensal
                WHERE id_projeto=%s AND id_orientador=%s AND mes_referencia=%s
                LIMIT 1
            """, (id_projeto, id_orientador, mes_ref))
            return bool(cursor.fetchone())
        finally:
            cursor.close()
