from typing import List, Optional
from datetime import date
from app.core.models.relatorio_mensal import RelatorioMensalOut, PendenciaOut, RelatorioMensalSecretariaOut, PendenciaSecretariaOut
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

    def listar_todos_por_mes(self, mes_ref: date) -> list[RelatorioMensalSecretariaOut]:
        c = self.db_conn.cursor()
        try:
            c.execute("""
                SELECT rm.id_relatorio,
                       p.id_projeto,
                       p.titulo_projeto,
                       o.nome_completo AS orientador_nome,
                       rm.mes_referencia,
                       rm.ok,
                       rm.observacao,
                       rm.confirmado_em
                  FROM tb_relatorio_mensal rm
                  JOIN tb_novo_projeto p ON p.id_projeto = rm.id_projeto
                  LEFT JOIN tb_cadastro_orientador o ON o.id_orientador = p.id_orientador
                 WHERE rm.mes_referencia = %s
              ORDER BY rm.confirmado_em DESC
            """, (mes_ref,))
            rows = c.fetchall()
            out = []
            for r in rows:
                out.append(RelatorioMensalSecretariaOut(
                    id_relatorio=r[0],
                    id_projeto=r[1],
                    titulo_projeto=r[2],
                    orientador_nome=r[3],
                    mes=r[4].strftime("%Y-%m"),
                    ok=bool(r[5]),
                    observacao=r[6],
                    confirmado_em=r[7]
                ))
            return out
        finally:
            c.close()

    def listar_pendentes_por_mes(self, mes_ref: date) -> list[PendenciaSecretariaOut]:
        c = self.db_conn.cursor()
        try:
            c.execute("""
                SELECT p.id_projeto,
                       p.titulo_projeto,
                       o.nome_completo AS orientador_nome
                  FROM tb_novo_projeto p
             LEFT JOIN tb_cadastro_orientador o ON o.id_orientador = p.id_orientador
             LEFT JOIN tb_relatorio_mensal rm
                       ON rm.id_projeto = p.id_projeto
                      AND rm.mes_referencia = %s
                 WHERE rm.id_relatorio IS NULL
              ORDER BY p.id_projeto DESC
            """, (mes_ref,))
            rows = c.fetchall()
            return [
                PendenciaSecretariaOut(
                    id_projeto=r[0],
                    titulo_projeto=r[1],
                    orientador_nome=r[2],
                    mes=mes_ref.strftime("%Y-%m")
                ) for r in rows
            ]
        finally:
            c.close()