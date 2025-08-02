# backend/app/config.py
import asyncio, os
from pathlib import Path
from dotenv import load_dotenv

def load_config():
    if os.name == "nt":                   # Windows only
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    os.environ.setdefault("WIDTH", "1024")
    os.environ.setdefault("HEIGHT", "768")
    os.environ.setdefault("DISPLAY_NUM", "1")

    # Look for .env next to this file or one directory up
    for candidate in (Path(__file__).parent / ".env",
                    Path(__file__).parent.parent / ".env"):
        if candidate.exists():
            load_dotenv(candidate)
            break
