from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from schemas import UserCreate, Token
from services import auth_service

# --- Authentication Endpoints ---
# שכבת ה-HTTP בלבד: מקבלת בקשה, קוראת לסרוויס ומחזירה תשובה

router = APIRouter()


@router.post("/register")
def register_user(user: UserCreate):
    """נתיב ליצירת משתמש חדש במערכת"""
    auth_service.register_user(user.email, user.password)
    return {"message": "User registered successfully"}


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    access_token = auth_service.login_user(form_data.username, form_data.password)
    return {"access_token": access_token, "token_type": "bearer"}
