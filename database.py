import sqlite3

DB_FILE = "materials.db"

def get_db_connection():
    # יצירת חיבור למסד הנתונים
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. יצירת טבלת משתמשים
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # 2. יצירת טבלת חומרים (מותאמת למודל הקיים שלך + קישור למשתמש)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institution TEXT,
            course_name TEXT,
            topic TEXT,
            material_type TEXT,
            uploader_name TEXT,
            contact_email TEXT,
            availability TEXT,
            year TEXT,
            semester TEXT,
            lecturer TEXT,
            material_format TEXT,
            file_path TEXT,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database and tables initialized successfully!")