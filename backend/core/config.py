# backend/core/config.py
"""
AdaalAI — Central configuration
Reads from .env (or environment variables).
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # ── App ────────────────────────────────────────────────────────────────────
    APP_NAME        : str  = os.getenv("APP_NAME", "AdaalAI")
    APP_VERSION     : str  = os.getenv("APP_VERSION", "1.0.0")
    DEBUG           : bool = os.getenv("DEBUG", "true").lower() == "true"

    # ── LLM ───────────────────────────────────────────────────────────────────
    LLM_PROVIDER    : str  = os.getenv("LLM_PROVIDER", "groq")
    LLM_MODEL       : str  = os.getenv("LLM_MODEL", "llama3-8b-8192")
    LLM_TEMPERATURE : float= float(os.getenv("LLM_TEMPERATURE", "0.1"))
    GROQ_API_KEY    : str  = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY  : str  = os.getenv("OPENAI_API_KEY", "")

    # ── Embeddings ────────────────────────────────────────────────────────────
    EMBEDDING_MODEL : str  = os.getenv(
        "EMBEDDING_MODEL", "intfloat/multilingual-e5-large"
    )

    # ── Paths ─────────────────────────────────────────────────────────────────
    # Two levels up from backend/core/ → project root
    BASE_DIR        : str  = os.path.dirname(
                                 os.path.dirname(
                                     os.path.dirname(os.path.abspath(__file__))
                                 )
                             )
    CHROMA_DB_PATH  : str  = os.path.join(BASE_DIR, "data", "chroma_db")
    PPC_DATA_PATH   : str  = os.path.join(BASE_DIR, "data", "ppc_sections.json")
    JUDGMENTS_PATH  : str  = os.path.join(BASE_DIR, "data", "judgments.json")
    CASE_DATA_PATH  : str  = os.path.join(BASE_DIR, "data", "cases.json")
    MODEL_SAVE_PATH : str  = os.path.join(BASE_DIR, "data", "priority_model.json")

    # ── Server ────────────────────────────────────────────────────────────────
    HOST            : str  = os.getenv("HOST", "0.0.0.0")
    PORT            : int  = int(os.getenv("PORT", "8000"))

    # ── CORS ──────────────────────────────────────────────────────────────────
    CORS_ORIGINS    : list = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")

settings = Settings()
