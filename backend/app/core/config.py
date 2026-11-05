import os
import json
import ast
from typing import List, Union
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Diabetes Multi-Agent AI Support System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-jwt-key-for-diabetes-multi-agent-system-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # SQLite local fallback by default, or PostgreSQL if configured
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'diabetes_system.db'))}"
    )
    
    # External AI Provider settings
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "local_demo") # local_demo | openai | gemini | ollama
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    
    CORS_ORIGINS: Union[str, List[str]] = ["*"]
    
    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        if isinstance(self.CORS_ORIGINS, str):
            val = self.CORS_ORIGINS.strip()
            if val.startswith("[") and val.endswith("]"):
                try:
                    return ast.literal_eval(val)
                except Exception:
                    pass
            return [i.strip() for i in val.split(",") if i.strip()]
        return ["*"]
    
    # ML Models path
    SAVED_MODELS_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml", "saved_models"))
    RAW_DATASET_PATH: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml-training", "datasets", "raw", "diabetes_prediction_dataset.csv"))
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

