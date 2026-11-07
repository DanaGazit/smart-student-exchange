from fastapi import HTTPException
from app.core import security
from app.repositories import users_repository

# הלוגיקה של הרשמה והתחברות


def register_user(email: str, password: str) -> None:
    if users_repository.get_user_by_email(email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # שומרים רק את ה-hash, אף פעם לא את הסיסמה עצמה
    users_repository.create_user(email, security.get_password_hash(password))


def login_user(email: str, password: str) -> str:
    """בודקת מייל וסיסמה ומחזירה JWT"""
    user = users_repository.get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not security.verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect password")

    return security.create_access_token(data={"sub": user["email"]})
