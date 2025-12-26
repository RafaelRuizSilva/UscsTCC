from typing import List
from app.core.ports.output.porta_upd_aluno_projeto import IProjetoGateway


class ProjetoGateway(IProjetoGateway):
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def projeto_existe(self, id_projeto: int) -> bool:
        cursor = self.db_conn.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM tb_novo_projeto WHERE id_projeto = %s LIMIT 1",
                (id_projeto,),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()

    def listar_ids_alunos_ativos(self, id_projeto: int) -> List[int]:
        cursor = self.db_conn.cursor()
        try:
            cursor.execute(
                """
                SELECT id_aluno
                  FROM tb_projeto_aluno
                 WHERE id_projeto = %s
                   AND status_aluno = TRUE
                """,
                (id_projeto,),
            )
            rows = cursor.fetchall()
            return [r[0] for r in rows]
        finally:
            cursor.close()

    def aluno_ativo_em_outro_projeto(self, id_aluno: int, id_projeto_atual: int) -> bool:
        cursor = self.db_conn.cursor()
        try:
            cursor.execute(
                """
                SELECT 1
                  FROM tb_projeto_aluno
                 WHERE id_aluno = %s
                   AND id_projeto <> %s
                   AND status_aluno = TRUE
                 LIMIT 1
                """,
                (id_aluno, id_projeto_atual),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()

    def upsert_status_aluno(self, id_projeto: int, id_aluno: int, status: bool) -> None:
        """
        Cria o vínculo se não existir; se existir, apenas atualiza o status.
        Requer UNIQUE (id_aluno, id_projeto).
        """
        cursor = self.db_conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO tb_projeto_aluno (id_aluno, id_projeto, status_aluno)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    status_aluno = VALUES(status_aluno)
                """,
                (id_aluno, id_projeto, bool(status)),
            )
            self.db_conn.commit()
        finally:
            cursor.close()

    def set_status_aluno(self, id_projeto: int, id_aluno: int, status: bool) -> None:
        cursor = self.db_conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE tb_projeto_aluno
                   SET status_aluno = %s
                 WHERE id_projeto = %s
                   AND id_aluno   = %s
                """,
                (bool(status), id_projeto, id_aluno),
            )
            self.db_conn.commit()
        finally:
            cursor.close()

    def listar_alunos_ativos_detalhado(self, id_projeto: int):
        cursor = self.db_conn.cursor()
        try:
            cursor.execute(
                """
                SELECT a.id_aluno,
                       a.nome_completo,
                       a.email,
                       a.cpf,
                       a.possui_trabalho_remunerado,
                       p.status_aluno,
                       p.created_at
                FROM tb_projeto_aluno p
                         JOIN tb_cadastro_aluno a ON a.id_aluno = p.id_aluno
                WHERE p.id_projeto = %s
                  AND p.status_aluno = TRUE
                ORDER BY p.created_at ASC
                """,
                (id_projeto,),
            )

            rows = cursor.fetchall()
            return [
                {
                    "id_aluno": r[0],
                    "nome_aluno": r[1],
                    "email": r[2],
                    "cpf": r[3],
                    "possui_trabalho_remunerado": bool(r[4]),
                    "status_aluno": bool(r[5]),
                    "selecionado_em": r[6].isoformat() if r[6] else None,
                }
                for r in rows
            ]
        finally:
            cursor.close()

    def get_projeto_selecionado_completo_por_aluno(self, id_aluno: int):
        cursor = self.db_conn.cursor()
        try:
            cursor.execute(
                """
                SELECT A.id_projeto,
                       A.cod_projeto,
                       A.titulo_projeto,
                       A.resumo,
                       A.id_orientador,
                       B.nome_completo                           AS orientador,
                       B.email                                   AS orientador_email,
                       A.id_campus,
                       C.campus,

                       IF(A.ideia_inicial IS NULL, 0, 1)         AS has_ideia_inicial,
                       IF(A.ideia_inicial_pdf IS NULL, 0, 1)     AS has_ideia_inicial_pdf,
                       IF(A.mon_parcial_docx_file IS NULL, 0, 1) AS has_mon_parcial_docx,
                       IF(A.mon_parcial_pdf_file IS NULL, 0, 1)  AS has_mon_parcial_pdf,
                       IF(A.mon_final_docx_file IS NULL, 0, 1)   AS has_mon_final_docx,
                       IF(A.mon_final_pdf_file IS NULL, 0, 1)    AS has_mon_final_pdf,

                       A.concluido,

                       (SELECT COUNT(*)
                        FROM tb_projeto_aluno pa
                        WHERE pa.id_projeto = A.id_projeto)      AS total_inscritos

                FROM tb_projeto_aluno PA
                         JOIN tb_novo_projeto A ON A.id_projeto = PA.id_projeto
                         JOIN tb_cadastro_orientador B ON B.id_orientador = A.id_orientador
                         JOIN tb_campus C ON C.id_campus = A.id_campus

                WHERE PA.id_aluno = %s
                  AND PA.status_aluno = TRUE LIMIT 1
                """,
                (id_aluno,),
            )

            row = cursor.fetchone()
            if not row:
                return None

            return {
                "id_projeto": row[0],
                "cod_projeto": row[1],
                "titulo_projeto": row[2],
                "resumo": row[3],
                "id_orientador": row[4],
                "orientador": row[5],
                "orientador_email": row[6],
                "id_campus": row[7],
                "campus": row[8],

                "has_ideia_inicial": bool(row[9]),
                "has_ideia_inicial_pdf": bool(row[10]),
                "has_mon_parcial_docx": bool(row[11]),
                "has_mon_parcial_pdf": bool(row[12]),
                "has_mon_final_docx": bool(row[13]),
                "has_mon_final_pdf": bool(row[14]),

                "concluido": bool(row[15]),
                "total_inscritos": row[16],
            }

        finally:
            cursor.close()