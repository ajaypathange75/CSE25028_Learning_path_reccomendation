import os
from pathlib import Path
from pydantic import BaseModel

# Suppress Windows joblib Loky CPU core count warning across the application
os.environ.setdefault("LOKY_MAX_CPU_COUNT", str(os.cpu_count() or 4))

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseModel):
    APP_NAME: str = "Career Path Recommendation & Personalized Learning System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    
    # Secret Key
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-career-path-ai-key-change-in-prod-2026")
    SESSION_COOKIE_NAME: str = "career_session_token"
    SESSION_MAX_AGE_SECONDS: int = 60 * 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'career_learning.db'}")
    
    # ML & Preprocessing paths (relative to BASE_DIR)
    DATASET_DIR: Path = BASE_DIR / "dataset"
    ENCODING_MAPPING_PATH: Path = DATASET_DIR / "career_path_encoding_mappings.json"
    MODELS_DIR: Path = BASE_DIR / "Models"
    VOTING_MODEL_PATH: Path = MODELS_DIR / "vot_model.sav"
    XGB_MODEL_PATH: Path = MODELS_DIR / "xgb_model.sav"
    
    # Gemma 3:1B & Ollama Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    GEMMA_MODEL_ID: str = os.getenv("GEMMA_MODEL_ID", "gemma3:1b")
    OLLAMA_TIMEOUT_SECONDS: float = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "90.0"))
    
    # Bayesian Knowledge Tracing (BKT) Hyperparameters
    BKT_DEFAULT_P_L0: float = 0.20   # Prior probability of knowing concept
    BKT_DEFAULT_P_TRANSIT: float = 0.15 # Learning transition probability
    BKT_DEFAULT_P_GUESS: float = 0.25   # Guessing probability (4 options)
    BKT_DEFAULT_P_SLIP: float = 0.10    # Slip probability (knew it but made mistake)
    
    # Competency Thresholds
    COMPETENCY_MASTERED_THRESHOLD: float = 0.70
    COMPETENCY_DEVELOPING_THRESHOLD: float = 0.40

settings = Settings()
