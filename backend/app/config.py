import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Expiry Copilot"
    API_V1_STR: str = "/api/v1"
    
    # JWT Auth Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-expiry-copilot-key-for-jwt-tokens-hackathon-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week for development demo ease
    
    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:////tmp/expiry_copilot.db" if os.getenv("VERCEL") == "1" else "sqlite:///./expiry_copilot.db")
    
    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Google OAuth Settings
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    
    # Virtual Date configuration
    VIRTUAL_DATE_FILE: str = "virtual_date_offset.txt"
    
    class Config:
        case_sensitive = True

settings = Settings()

# Helper functions to get/set simulated date offset (in days from actual system date)
def get_virtual_days_offset() -> int:
    # Check default file first, then fall back to /tmp/ for serverless environments
    for path in [settings.VIRTUAL_DATE_FILE, os.path.join("/tmp", settings.VIRTUAL_DATE_FILE)]:
        try:
            if os.path.exists(path):
                with open(path, "r") as f:
                    content = f.read().strip()
                    if content:
                        return int(content)
        except Exception:
            pass
    return 0

def set_virtual_days_offset(days: int):
    # Try saving to the default file path
    try:
        with open(settings.VIRTUAL_DATE_FILE, "w") as f:
            f.write(str(days))
        return
    except Exception as e:
        print(f"Error saving virtual days offset to default path: {e}")
    
    # Fallback to /tmp/ path (e.g., on Vercel's read-only filesystem)
    try:
        tmp_path = os.path.join("/tmp", settings.VIRTUAL_DATE_FILE)
        with open(tmp_path, "w") as f:
            f.write(str(days))
    except Exception as e:
        print(f"Error saving virtual days offset to /tmp: {e}")
