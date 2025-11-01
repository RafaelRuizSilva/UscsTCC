from app.core.models.curso import Curso

class CursoRepository:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create(self, curso: Curso) -> int:
        cursor = self.db_conn.cursor()
        query = "INSERT INTO tb_curso (nome) VALUES (%s)"
        cursor.execute(query, (curso.nome,))
        self.db_conn.commit()
        return cursor.lastrowid

    def get_all(self) -> list[dict]:
        cursor = self.db_conn.cursor()
        query = "SELECT id_curso, nome FROM tb_curso"
        cursor.execute(query)
        rows = cursor.fetchall()
        return [{"id_curso": row[0], "nome": row[1]} for row in rows]

    def get_by_id(self, curso_id: int) -> dict:
        cursor = self.db_conn.cursor()
        query = "SELECT id_curso, nome FROM tb_curso WHERE id_curso = %s"
        cursor.execute(query, (curso_id,))
        row = cursor.fetchone()
        if row:
            return {"id_curso": row[0], "nome": row[1]}
        return None

    def update(self, curso_id: int, curso: Curso) -> None:
        cursor = self.db_conn.cursor()
        query = "UPDATE tb_curso SET nome = %s WHERE id_curso = %s"
        cursor.execute(query, (curso.nome, curso_id))
        self.db_conn.commit()
        if cursor.rowcount == 0:
            raise ValueError("Curso não encontrado.")

    def delete(self, curso_id: int) -> None:
        cursor = self.db_conn.cursor()
        query = "DELETE FROM tb_curso WHERE id_curso = %s"
        cursor.execute(query, (curso_id,))
        self.db_conn.commit()
        if cursor.rowcount == 0:
            raise ValueError("Curso não encontrado.")