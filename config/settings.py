import os
from dotenv import load_dotenv
import pydantic

# Load environment variables from .env file
load_dotenv()

# Try to import BaseSettings from pydantic (v1) or pydantic-settings (v2). If neither
# is available, we fall back to a lightweight env-based Settings implementation.
BaseSettings = None
PYDANTIC_V2 = False
try:
    from pydantic import BaseSettings as _BaseSettings
    BaseSettings = _BaseSettings
    PYDANTIC_V2 = not getattr(pydantic, '__version__', '').startswith('2')
except Exception:
    try:
        from pydantic_settings import BaseSettings as _BaseSettings
        BaseSettings = _BaseSettings
        PYDANTIC_V2 = True
    except Exception:
        BaseSettings = None


if BaseSettings is None:
    # lightweight fallback when pydantic is not installed/usable
    class Settings:
        OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
        EMBEDDING_MODEL: str = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-mpnet-base-v2')
        CHUNK_SIZE_TOKENS: int = int(os.getenv('CHUNK_SIZE_TOKENS', '900'))
        CHUNK_OVERLAP_TOKENS: int = int(os.getenv('CHUNK_OVERLAP_TOKENS', '300'))
        SIMILARITY_THRESHOLD: float = float(os.getenv('SIMILARITY_THRESHOLD', '0.35'))
        TOP_K: int = int(os.getenv('TOP_K', '8'))

    settings = Settings()
else:
    class Settings(BaseSettings):
        OPENAI_API_KEY: str = ""
        EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"
        CHUNK_SIZE_TOKENS: int = 900
        CHUNK_OVERLAP_TOKENS: int = 300
        SIMILARITY_THRESHOLD: float = 0.35
        TOP_K: int = 8

        # support env_file for both pydantic v1 and v2
        if getattr(pydantic, '__version__', '').startswith('2'):
            model_config = {"env_file": ".env"}
        else:
            class Config:
                env_file = ".env"


    settings = Settings()
