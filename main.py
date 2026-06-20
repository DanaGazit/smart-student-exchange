from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import uuid
from dotenv import load_dotenv
import base64
import jwt
from io import BytesIO
from PIL import Image
import database
import auth
import ai_service
import logging

# הגדרת מערכת הלוגים של השרת
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
# Initialize environment variables and AI client
load_dotenv()

app = FastAPI()
database.init_db()
# Configure local storage for uploaded files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/downloads", StaticFiles(directory=UPLOAD_DIR), name="downloads")

# הגדרת סכמת האבטחה לקבלת הטוקן
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- Pydantic Models ---

class StudyMaterial(BaseModel):
    institution: str
    course_name: str
    topic: str
    material_type: str
    uploader_name: str
    contact_email: str
    availability: str
    year: str
    semester: str
    lecturer: Optional[str] = None
    material_format: Optional[str] = None
    file_path: Optional[str] = None
    user_id: Optional[int] = None # שדה חדש לקישור למשתמש

class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Authentication Endpoints ---

@app.post("/register")
def register_user(user: UserCreate):
    """נתיב ליצירת משתמש חדש במערכת"""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    try:
        # בדיקה אם המייל כבר קיים
        cursor.execute("SELECT * FROM users WHERE email = ?", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
            
        # הצפנת סיסמה ושמירה
        hashed_pw = auth.get_password_hash(user.password)
        cursor.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (user.email, hashed_pw))
        conn.commit()
        return {"message": "User registered successfully"}
    finally:
        conn.close()


@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = ?", (form_data.username,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        # הודעה ספציפית שהמשתמש לא נמצא
        raise HTTPException(status_code=404, detail="User not found")

    if not auth.verify_password(form_data.password, user["password_hash"]):
        # הודעה ספציפית שהסיסמה שגויה
        raise HTTPException(status_code=401, detail="Incorrect password")

    access_token = auth.create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Materials Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Smart Student Exchange API is running."}

@app.get("/materials")
def get_all_materials():
    """Retrieves all study materials from the database."""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM materials")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/materials")
def save_material(material: StudyMaterial, token: str = Depends(oauth2_scheme)):
    """Saves a new study material record to the database."""
    # --- שלב 1: אימות ופענוח הטוקן ונורמליזציה של המידע ---
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        raw_email = payload.get("sub")
        
        if raw_email is None:
            raise HTTPException(status_code=401, detail="Invalid token - No user identified")
            
        # נורמליזציה: מורידים רווחים שקופים מצדדי המחרוזת והופכים לאותיות קטנות
        clean_user_email = str(raw_email).strip().lower()
        
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # --- שלב 2: שמירת החומר עם הזיהוי המאומת והנקי ---
    conn = database.get_db_connection()
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
        clean_user_email  # הכנסת המייל המנורמל
    ))
    
    conn.commit()
    conn.close()
    return {"message": "Material saved successfully."}

@app.post("/analyze-material")
async def analyze_material(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        file_ext = file.filename.split('.')[-1].lower() if file.filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        save_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(save_path, "wb") as f:
            f.write(file_bytes)
            
        download_url = f"/downloads/{unique_filename}"
        
        ai_result = ai_service.analyze_document(file_bytes, file_ext)
        ai_result["file_path"] = download_url
        
        return {"message": "Analysis successful", "data": ai_result}
        
    except ValueError as ve:
        return {"error": str(ve)}
    except Exception as e:
        logger.error(f"Analyze API failed: {str(e)}")
        return {"error": f"שגיאה בעיבוד הקובץ: {str(e)}"}    
@app.delete("/materials/{material_id}")
def delete_material(material_id: int, token: str = Depends(oauth2_scheme)):
    # 1. אימות טוקן
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        clean_token_email = str(payload.get("sub")).strip().lower()
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    conn = database.get_db_connection()
    cursor = conn.cursor()

    try:
        # 2. בדיקת בעלות
        cursor.execute("SELECT user_id FROM materials WHERE id = ?", (material_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Material not found")
            
        if str(row["user_id"]).strip().lower() != clean_token_email:
            raise HTTPException(status_code=403, detail="Not authorized")

        # 3. מחיקה בפועל
        cursor.execute("DELETE FROM materials WHERE id = ?", (material_id,))
        conn.commit()
        return {"message": "Material deleted successfully"}
        
    except HTTPException:
        raise # מעביר הלאה שגיאות 403 ו-404 בצורה תקינה
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"DB Error: {e}")
    finally:
        
        conn.close()


class UpdateMaterial(BaseModel):
    institution: str
    course_name: str
    topic: str
    material_type: str
    availability: str
    year: str
    semester: str
    lecturer: str
    material_format: str

@app.put("/materials/{material_id}")
def update_material(material_id: int, updated_data: UpdateMaterial, token: str = Depends(oauth2_scheme)):
    # אימות טוקן ונורמליזציה (כמו שעשינו)
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        clean_token_email = str(payload.get("sub")).strip().lower()
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    # בדיקת בעלות
    cursor.execute("SELECT user_id FROM materials WHERE id = ?", (material_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Material not found")
        
    if str(row["user_id"]).strip().lower() != clean_token_email:
        conn.close()
        raise HTTPException(status_code=403, detail="Not authorized")

    # --- התיקון הקריטי: וודאי שכל ה-? תואמים למספר השדות ---
    try:
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
            updated_data.institution, 
            updated_data.course_name, 
            updated_data.topic, 
            updated_data.material_type,
            updated_data.availability, 
            updated_data.year, 
            updated_data.semester, 
            updated_data.lecturer, 
            updated_data.material_format, 
            material_id
        ))
        conn.commit()
        logger.info(f"Material {material_id} was successfully updated by {clean_token_email}")
    except Exception as e:
        logger.error(f"Database update failed for material {material_id}: {e}")
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()
    
    return {"message": "Updated"}