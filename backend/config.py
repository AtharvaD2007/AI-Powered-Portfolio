import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from backend or root directory
BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

# Try backend/.env first, then root .env
if (BASE_DIR / ".env").exists():
    load_dotenv(BASE_DIR / ".env")
elif (PROJECT_DIR / ".env").exists():
    load_dotenv(PROJECT_DIR / ".env")
else:
    load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "ai-portfolio-secret-key-2026")
    
    # SQLite Database
    DATA_DIR = BASE_DIR / "data"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(DATA_DIR / "portfolio.db"))
    
    # Gemini AI configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Google Sheets configuration
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
    GOOGLE_SHEETS_CREDENTIALS_JSON = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON", "")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

    @classmethod
    def is_gemini_configured(cls) -> bool:
        return bool(cls.GEMINI_API_KEY and len(cls.GEMINI_API_KEY.strip()) > 5)

    @classmethod
    def is_google_sheets_configured(cls) -> bool:
        if cls.GOOGLE_APPLICATION_CREDENTIALS and os.path.exists(cls.GOOGLE_APPLICATION_CREDENTIALS):
            return True
        if cls.GOOGLE_SHEETS_CREDENTIALS_JSON:
            # Check if it's a valid path or valid JSON
            if os.path.exists(cls.GOOGLE_SHEETS_CREDENTIALS_JSON):
                return True
            try:
                data = json.loads(cls.GOOGLE_SHEETS_CREDENTIALS_JSON)
                return isinstance(data, dict) and "client_email" in data
            except Exception:
                return False
        return False
