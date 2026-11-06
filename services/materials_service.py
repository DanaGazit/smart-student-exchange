import os
import uuid
import logging
from fastapi import HTTPException
from schemas import StudyMaterial, UpdateMaterial
from repositories import materials_repository
from services import ai_service

logger = logging.getLogger(__name__)

# תיקיית הקבצים שהועלו (מוגשת החוצה דרך /downloads ב-main.py)
UPLOAD_DIR = "uploads"


def list_materials() -> list:
    return materials_repository.get_all_materials()


def create_material(material: StudyMaterial, user_email: str) -> None:
    # הבעלים נלקח מהטוקן ולא מגוף הבקשה, כדי שאי אפשר יהיה להתחזות
    materials_repository.insert_material(material, user_email)


def _check_owner(material_id: int, user_email: str) -> None:
    """בדיקת בעלות: 404 אם החומר לא קיים, 403 אם הוא לא של המשתמש"""
    owner = materials_repository.get_material_owner(material_id)

    if owner is None:
        raise HTTPException(status_code=404, detail="Material not found")

    if str(owner).strip().lower() != user_email:
        raise HTTPException(status_code=403, detail="Not authorized")


def update_material(material_id: int, data: UpdateMaterial, user_email: str) -> None:
    _check_owner(material_id, user_email)
    try:
        materials_repository.update_material(material_id, data)
        logger.info(f"Material {material_id} was successfully updated by {user_email}")
    except Exception as e:
        logger.error(f"Database update failed for material {material_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


def delete_material(material_id: int, user_email: str) -> None:
    _check_owner(material_id, user_email)
    try:
        materials_repository.delete_material(material_id)
    except Exception as e:
        logger.error(f"Database delete failed for material {material_id}: {e}")
        raise HTTPException(status_code=500, detail=f"DB Error: {e}")


def save_and_analyze_file(file_bytes: bytes, filename: str) -> dict:
    """
    שומרת את הקובץ בשם ייחודי (UUID) ושולחת אותו לניתוח AI.
    מחזירה את השדות שה-AI חילץ, יחד עם הנתיב להורדת הקובץ.
    """
    file_ext = filename.split('.')[-1].lower() if filename else 'jpg'
    unique_filename = f"{uuid.uuid4()}.{file_ext}"

    with open(os.path.join(UPLOAD_DIR, unique_filename), "wb") as f:
        f.write(file_bytes)

    ai_result = ai_service.analyze_document(file_bytes, file_ext)
    ai_result["file_path"] = f"/downloads/{unique_filename}"
    return ai_result
