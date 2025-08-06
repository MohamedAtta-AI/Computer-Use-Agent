from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Computer Use Agent"
    production: bool

    # DB Config
    db_host: str
    db_user: str
    db_pass: str
    db_name: str
    db_port: int

    # API Config
    anthropic_api_key: str

    class Config:
        env_file = env_file = Path(__file__).resolve().parent.parent.parent / ".env"

    @property
    def db_url(self):
        return f"postgresql+psycopg2://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"

@lru_cache()
def get_settings():
    return Settings()