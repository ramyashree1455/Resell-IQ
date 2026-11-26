import os
from pathlib import Path

# Absolute path to resell.db so all processes share the exact same database
BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "resell.db"
DEFAULT_DB_URL = f"sqlite:///{DB_FILE.as_posix()}"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

# AI / LLM Configuration (loaded from environment, never hardcoded)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

