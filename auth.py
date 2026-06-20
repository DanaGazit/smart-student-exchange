import os
from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is missing in .env file!")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
# משיכת זמן התפוגה של הטוקן (60 דקות כפי שהגדרת)
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

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
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # יצירת החותמת הקריפטוגרפית בעזרת PyJWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt