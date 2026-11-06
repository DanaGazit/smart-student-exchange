import database
from schemas import StudyMaterial, UpdateMaterial

# שכבת הגישה לנתונים של חומרי לימוד: רק SQL, בלי לוגיקה ובלי בדיקות הרשאה


def get_all_materials() -> list:
    conn = database.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM materials")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_material_owner(material_id: int):
    """מחזירה את המייל של מי שהעלה את החומר, או None אם החומר לא קיים"""
    conn = database.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM materials WHERE id = ?", (material_id,))
        row = cursor.fetchone()
        return row["user_id"] if row else None
    finally:
        conn.close()


def insert_material(material: StudyMaterial, owner_email: str) -> None:
    conn = database.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO materials (
                institution, course_name, topic, material_type, uploader_name,
                contact_email, availability, year, semester, lecturer, material_format, file_path, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            material.institution, material.course_name, material.topic, material.material_type,
            material.uploader_name, material.contact_email, material.availability,
            material.year, material.semester, material.lecturer, material.material_format,
            material.file_path,
            owner_email
        ))
        conn.commit()
    finally:
        conn.close()


def update_material(material_id: int, data: UpdateMaterial) -> None:
    conn = database.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE materials
            SET institution = ?,
                course_name = ?,
                topic = ?,
                material_type = ?,
                availability = ?,
                year = ?,
                semester = ?,
                lecturer = ?,
                material_format = ?
            WHERE id = ?
        ''', (
            data.institution, data.course_name, data.topic, data.material_type,
            data.availability, data.year, data.semester, data.lecturer, data.material_format,
            material_id
        ))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_material(material_id: int) -> None:
    conn = database.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM materials WHERE id = ?", (material_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
