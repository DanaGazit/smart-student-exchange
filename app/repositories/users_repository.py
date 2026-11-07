from app.core import database

# שכבת הגישה לנתונים של משתמשים: רק SQL, בלי לוגיקה


def get_user_by_email(email: str):
    conn = database.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        return cursor.fetchone()
    finally:
        conn.close()


def create_user(email: str, password_hash: str) -> None:
    conn = database.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, password_hash))
        conn.commit()
    finally:
        conn.close()
