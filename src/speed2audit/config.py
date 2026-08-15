import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Core settings
SPEED2AUDIT_ENV: str = os.getenv("SPEED2AUDIT_ENV", "development")
SPEED2AUDIT_LOG_LEVEL: str = os.getenv("SPEED2AUDIT_LOG_LEVEL", "INFO")
DATABASE_PATH: str = os.getenv("DATABASE_PATH", "speed2audit.db")

# Google Gemini
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

# WAHA (WhatsApp HTTP API)
WAHA_BASE_URL: str = os.getenv("WAHA_BASE_URL", "http://localhost:3000")
WAHA_SESSION: str = os.getenv("WAHA_SESSION", "default")
WAHA_API_KEY: str = os.getenv("WAHA_API_KEY", "")

# Humanization Constants (Fixed 15-40s delay)
MIN_HUMAN_DELAY_SECONDS: float = 15.0
MAX_HUMAN_DELAY_SECONDS: float = 40.0

# Safety Turn Limits
MAX_CONVERSATION_TURNS: int = 10
ABANDONMENT_TIMEOUT_MINUTES: int = 120

# Observability & Tracing (Arize Phoenix - Local)
PHOENIX_ENABLE: bool = os.getenv("PHOENIX_ENABLE", "true").lower() in ("true", "1", "yes")
PHOENIX_COLLECTOR_ENDPOINT: str = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://127.0.0.1:6006")
