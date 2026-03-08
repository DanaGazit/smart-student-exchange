from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import uuid
import sqlite3
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Initialize environment variables and AI client
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else None

app = FastAPI()

# Configure local storage for uploaded files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/downloads", StaticFiles(directory=UPLOAD_DIR), name="downloads")

# Database configuration
DB_FILE = "materials.db"

def init_db():
    """Initializes the SQLite database and creates the materials table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
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
            file_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Pydantic model for data validation
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

@app.get("/")
def read_root():
    return {"message": "Smart Student Exchange API is running."}

@app.get("/materials")
def get_all_materials():
    """Retrieves all study materials from the database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM materials")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/materials")
def save_material(material: StudyMaterial):
    """Saves a new study material record to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO materials (
            institution, course_name, topic, material_type, uploader_name,
            contact_email, availability, year, semester, lecturer, material_format, file_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        material.institution, material.course_name, material.topic, material.material_type,
        material.uploader_name, material.contact_email, material.availability,
        material.year, material.semester, material.lecturer, material.material_format, material.file_path
    ))
    conn.commit()
    conn.close()
    return {"message": "Material saved successfully."}

@app.post("/analyze-material")
async def analyze_material(file: UploadFile = File(...)):
    """
    Receives an uploaded file, saves it locally, and uses Google's Gemini AI 
    to extract structural metadata (course name, topic, format, etc.).
    """
    try:
        if not client:
            return {"error": "AI API Key is missing or invalid configuration."}

        # Read and save the file securely with a UUID
        image_bytes = await file.read()
        file_ext = file.filename.split('.')[-1] if file.filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        save_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(save_path, "wb") as f:
            f.write(image_bytes)
            
        download_url = f"/downloads/{unique_filename}"
        
        # Construct the prompt for the AI model
        prompt = """
        Analyze this document or image of a student's study material.
        Return ONLY a valid JSON object with the exact following keys and string values:
        - course_name: the precise name of the academic course in Hebrew. Read the text carefully.
        - topic: the specific topic of this page, written in Hebrew.
        - material_type: classify exactly as 'סיכום', 'מבחן', 'שיעורי בית', or 'דף נוסחאות'.
        - year: the academic year written (e.g., '2023', '2024', 'תשפ"ד'). If not found, write 'לא צוין'.
        - semester: the semester written (e.g., 'א', 'ב', 'קיץ'). If not found, write 'לא צוין'.
        - lecturer: the name of the lecturer if written. If not found, leave empty string "".
        - material_format: classify as 'מודפס' (typed) or 'בכתב יד' (handwritten). If unsure, leave empty "".
        Do not include any markdown formatting like ```json.
        """
        
        safe_mime_type = file.content_type or "image/jpeg"
        
        # Invoke Gemini API
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type=safe_mime_type)
            ]
        )
        
        # Parse AI response
        safe_text = response.text or "{}"
        ai_result = json.loads(safe_text.strip())
        ai_result["file_path"] = download_url
        
        return {"message": "Analysis successful", "data": ai_result}
        
    except Exception as e:
        return {"error": str(e)}