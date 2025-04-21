import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

def get_env(key: str, default: str | None = None) -> str | None:
    return os.getenv(key, default)
