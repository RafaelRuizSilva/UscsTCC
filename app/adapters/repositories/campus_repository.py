from app.core.models.campus import Campus

class CampusRepository:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create(self, campus: Campus) -> int:
        cursor = self.db_conn.cursor()
        query = "INSERT INTO tb_campus (campus) VALUES (%s)"
        cursor.execute(query, (campus.campus,))
        self.db_conn.commit()
        return cursor.lastrowid

    def get_all(self) -> list[dict]:
        cursor = self.db_conn.cursor()
        query = "SELECT id_campus, campus FROM tb_campus"
        cursor.execute(query)
        rows = cursor.fetchall()
        return [{"id_campus": row[0], "campus": row[1]} for row in rows]

    def get_by_id(self, campus_id: int) -> dict:
        cursor = self.db_conn.cursor()
        query = "SELECT id_campus, campus FROM tb_campus WHERE id_campus = %s"
        cursor.execute(query, (campus_id,))
        row = cursor.fetchone()
        if row:
            return {"id_campus": row[0], "campus": row[1]}
        return None

    def update(self, campus_id: int, campus: Campus) -> None:
        cursor = self.db_conn.cursor()
        query = "UPDATE tb_campus SET campus = %s WHERE id_campus = %s"
        cursor.execute(query, (campus.campus, campus_id))
        self.db_conn.commit()
        if cursor.rowcount == 0:
            raise ValueError("Campus não encontrado.")

    def delete(self, campus_id: int) -> None:
        cursor = self.db_conn.cursor()
        query = "DELETE FROM tb_campus WHERE id_campus = %s"
        cursor.execute(query, (campus_id,))
        self.db_conn.commit()
        if cursor.rowcount == 0:
            raise ValueError("Campus não encontrado.")