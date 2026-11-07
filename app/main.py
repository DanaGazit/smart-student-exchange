import os
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core import database
from app.core.config import UPLOAD_DIR
from app.api.routers import auth_router, materials_router

# הגדרת מערכת הלוגים של השרת
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

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
