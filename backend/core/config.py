from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Computer Use Agent"
    production: bool

    # Server Config
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    
    # CORS Config
    frontend_url: str = "http://localhost:5173"
    frontend_alt_url: str = "http://127.0.0.1:5173"
    
    # VNC Config
    vnc_web_port: int = 6080
    vnc_raw_port: int = 5900

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
    
    @property
    def cors_origins(self):
        """Get CORS origins based on environment"""
        if self.production:
            return [self.frontend_url]
        return [self.frontend_url, self.frontend_alt_url]

@lru_cache()
def get_settings():
    return Settings()