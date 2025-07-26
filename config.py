import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "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")
    MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
    DATABASE_URL = "sqlite:///./jarvis.db"
    UPLOAD_DIR = "uploads"
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB 