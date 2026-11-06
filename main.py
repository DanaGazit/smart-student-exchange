import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import database
from routers import auth_router, materials_router
from services.materials_service import UPLOAD_DIR

# הגדרת מערכת הלוגים של השרת
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
# Initialize environment variables
load_dotenv()

app = FastAPI()
database.init_db()

# Configure local storage for uploaded files
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/downloads", StaticFiles(directory=UPLOAD_DIR), name="downloads")

# חיבור ה-routers: כל קבוצת endpoints נמצאת בקובץ משלה בתיקיית routers
app.include_router(auth_router.router)
app.include_router(materials_router.router)


@app.get("/")
def read_root():
    return {"message": "Smart Student Exchange API is running."}
