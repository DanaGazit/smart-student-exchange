from typing import Optional
from pydantic import BaseModel

# --- Pydantic Models ---
# המבנה של הנתונים שנכנסים ויוצאים מה-API. FastAPI בודק אותם אוטומטית (ומחזיר 422 אם חסר שדה)


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
    user_id: Optional[int] = None  # לא בשימוש: הבעלים נקבע תמיד לפי הטוקן


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


class UserCreate(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
