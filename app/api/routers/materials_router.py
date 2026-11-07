import logging
from fastapi import APIRouter, Depends, UploadFile, File
from app.schemas import StudyMaterial, UpdateMaterial
from app.api.dependencies import get_current_user
from app.services import materials_service

logger = logging.getLogger(__name__)

# --- Materials Endpoints ---
# שכבת ה-HTTP בלבד. Depends(get_current_user) מאמת את הטוקן לפני שה-endpoint רץ

router = APIRouter()


@router.get("/materials")
def get_all_materials():
    """Retrieves all study materials from the database."""
    return materials_service.list_materials()


@router.post("/materials")
def save_material(material: StudyMaterial, user_email: str = Depends(get_current_user)):
    """Saves a new study material record to the database."""
    materials_service.create_material(material, user_email)
    return {"message": "Material saved successfully."}


@router.post("/analyze-material")
def analyze_material(file: UploadFile = File(...)):
    # def ולא async def: הקריאה ל-AI חוסמת, ו-FastAPI מריץ def ב-thread pool, כך שהשרת ממשיך לענות לאחרים
    try:
        file_bytes = file.file.read()
        ai_result = materials_service.save_and_analyze_file(file_bytes, file.filename)
        return {"message": "Analysis successful", "data": ai_result}

    except ValueError as ve:
        return {"error": str(ve)}
    except Exception as e:
        logger.error(f"Analyze API failed: {str(e)}")
        return {"error": f"שגיאה בעיבוד הקובץ: {str(e)}"}


@router.put("/materials/{material_id}")
def update_material(material_id: int, updated_data: UpdateMaterial, user_email: str = Depends(get_current_user)):
    materials_service.update_material(material_id, updated_data, user_email)
    return {"message": "Updated"}


@router.delete("/materials/{material_id}")
def delete_material(material_id: int, user_email: str = Depends(get_current_user)):
    materials_service.delete_material(material_id, user_email)
    return {"message": "Material deleted successfully"}
