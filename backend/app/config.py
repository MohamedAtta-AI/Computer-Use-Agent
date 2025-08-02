# backend/app/config.py
from pathlib import Path
from dotenv import load_dotenv

def load_config():
    # Look for .env next to this file or one directory up
    for candidate in (Path(__file__).parent / ".env",
                    Path(__file__).parent.parent / ".env"):
        if candidate.exists():
            load_dotenv(candidate)
            break
