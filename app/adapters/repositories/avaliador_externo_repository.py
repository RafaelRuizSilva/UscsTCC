from pymysql.err import IntegrityError
from app.core.models.avaliador_externo import AvaliadorExternoCreate
from app.core.ports.output.porta_avaliador_externo_repository import IAvaliadorExternoRepository

class AvaliadorExternoRepository(IAvaliadorExternoRepository):
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create(self, avaliador: AvaliadorExternoCreate) -> int:
        cursor = self.db_conn.cursor()

        try:
            query = """
                INSERT INTO TB_AVALIADOR_EXTERNO (nome, email, especialidade, subespecialidade, link_lattes)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                avaliador.nome,
                avaliador.email,
                avaliador.especialidade,
                avaliador.subespecialidade,
                avaliador.link_lattes
            ))
            self.db_conn.commit()
            return cursor.lastrowid

        except IntegrityError as err:
            if "duplicate entry" in str(err).lower():
                raise ValueError("E-mail já cadastrado.")
            raise

    def list_all(self) -> list[dict]:
        """
        Retorna todos os avaliadores externos.
        """
        cursor = self.db_conn.cursor()
        query = """
            SELECT id_avaliador, nome, email, especialidade, subespecialidade, link_lattes
            FROM TB_AVALIADOR_EXTERNO
            ORDER BY nome ASC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        # rows vem como tuplas -> mapeia para dicts que o front espera
        resultado = []
        for r in rows:
            resultado.append({
                "id": r[0],
                "nome": r[1],
                "email": r[2],
                "especialidade": r[3],
                "subespecialidade": r[4],
                "link_lattes": r[5],
            })
        return resultado

    def get_by_id(self, id_avaliador: int) -> dict | None:
        """
        Retorna um avaliador por ID ou None se não existir.
        """
        cursor = self.db_conn.cursor()
        query = """
            SELECT id_avaliador, nome, email, especialidade, subespecialidade, link_lattes
            FROM TB_AVALIADOR_EXTERNO
            WHERE id_avaliador = %s
        """
        cursor.execute(query, (id_avaliador,))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "nome": row[1],
            "email": row[2],
            "especialidade": row[3],
            "subespecialidade": row[4],
            "link_lattes": row[5],
        }

    def update(self, id_avaliador: int, avaliador: AvaliadorExternoCreate) -> None:
        """
        Atualiza um avaliador existente.
        """
        cursor = self.db_conn.cursor()
        try:
            query = """
                UPDATE TB_AVALIADOR_EXTERNO
                SET nome = %s,
                    email = %s,
                    especialidade = %s,
                    subespecialidade = %s,
                    link_lattes = %s
                WHERE id_avaliador = %s
            """
            cursor.execute(query, (
                avaliador.nome,
                avaliador.email,
                avaliador.especialidade,
                avaliador.subespecialidade,
                avaliador.link_lattes,
                id_avaliador
            ))
            self.db_conn.commit()
            if cursor.rowcount == 0:
                raise ValueError("Avaliador não encontrado.")
        except IntegrityError as err:
            if "duplicate entry" in str(err).lower():
                raise ValueError("E-mail já cadastrado.")
            raise

    def delete(self, id_avaliador: int) -> None:
        cursor = self.db_conn.cursor()
        query = "DELETE FROM TB_AVALIADOR_EXTERNO WHERE id_avaliador = %s"
        cursor.execute(query, (id_avaliador,))
        self.db_conn.commit()
        if cursor.rowcount == 0:
            raise ValueError("Avaliador não encontrado.")
        