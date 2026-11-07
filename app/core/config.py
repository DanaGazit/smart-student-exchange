"""Central configuration: every environment variable is read here, once."""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Security / JWT ---
SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is missing in .env file!")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# --- AI (Groq) ---
# מודל ה-AI (חייב לתמוך בתמונות). אפשר להחליף דרך .env בלי לשנות קוד
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

# --- Storage (relative to the working directory, i.e. the project root) ---
DB_FILE = os.getenv("DB_FILE", "materials.db")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
