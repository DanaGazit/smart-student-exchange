import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.core import config

# שולף את הטוקן מהכותרת Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    אימות הטוקן במקום אחד לכל ה-endpoints המוגנים.
    מחזירה את המייל של המשתמש המחובר (מנורמל), או זורקת 401.
    """
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        raw_email = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if raw_email is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # נורמליזציה: מורידים רווחים ומעבירים לאותיות קטנות, כדי שההשוואה לבעלים תהיה עקבית
    return str(raw_email).strip().lower()
