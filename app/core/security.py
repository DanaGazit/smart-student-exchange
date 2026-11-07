from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from app.core import config

# הגדרת אלגוריתם ההצפנה לסיסמאות
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    מקבלת סיסמה גלויה (למשל '123456') 
    ומחזירה מחרוזת מוצפנת בלתי הפיכה.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    מקבלת סיסמה שהוקלדה בהתחברות ואת הגיבוב ממסד הנתונים,
    ובודקת האם הם תואמים. מחזירה True או False.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """
    מקבלת מידע על המשתמש (כמו המייל שלו),
    אורזת אותו יחד עם תאריך תפוגה, וחותמת עליו עם המפתח הסודי ליצירת טוקן.
    """
    to_encode = data.copy()
    
    # חישוב הזמן שבו הטוקן יפוג (עוד 60 דקות מעכשיו)
    expire = datetime.now(timezone.utc) + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # יצירת החותמת הקריפטוגרפית בעזרת PyJWT
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt