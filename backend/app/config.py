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
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./expiry_copilot.db")
    
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
    try:
        if os.path.exists(settings.VIRTUAL_DATE_FILE):
            with open(settings.VIRTUAL_DATE_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return int(content)
    except Exception:
        pass
    return 0

def set_virtual_days_offset(days: int):
    try:
        with open(settings.VIRTUAL_DATE_FILE, "w") as f:
            f.write(str(days))
    except Exception as e:
        print(f"Error saving virtual days offset: {e}")
