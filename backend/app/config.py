"""
Configuration settings for the Computer Use Agent Backend
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_title: str = "Computer Use Agent API"
    api_version: str = "1.0.0"
    api_description: str = "A scalable backend for computer use agent session management"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Database Configuration
    database_url: str = Field(
        default="postgresql://user:password@localhost/computer_use_agent",
        description="PostgreSQL database connection URL"
    )
    
    # Redis Configuration
    redis_url: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL for caching and session storage"
    )
    
    # Anthropic API Configuration
    anthropic_api_key: str = Field(..., description="Anthropic API key")
    anthropic_model: str = Field(
        default="claude-sonnet-4-20250514",
        description="Default Anthropic model to use"
    )
    default_max_tokens: int = Field(
        default=4096,
        description="Default maximum tokens for model responses"
    )
    default_temperature: float = Field(
        default=1.0,
        description="Default temperature for model responses"
    )
    tool_timeout: float = Field(
        default=120.0,
        description="Default timeout for tool execution in seconds"
    )
    
    # VNC Configuration
    vnc_host: str = Field(default="localhost", description="VNC server host")
    vnc_port: int = Field(default=5900, description="VNC server port")
    vnc_password: Optional[str] = Field(default=None, description="VNC server password")
    
    # Security Configuration
    secret_key: str = Field(..., description="Secret key for JWT token generation")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="JWT token expiration time")
    
    # File Upload Configuration
    upload_dir: str = Field(default="./uploads", description="Directory for file uploads")
    max_file_size: int = Field(default=100 * 1024 * 1024, description="Maximum file size in bytes")
    
    # WebSocket Configuration
    websocket_ping_interval: int = Field(default=20, description="WebSocket ping interval in seconds")
    websocket_ping_timeout: int = Field(default=20, description="WebSocket ping timeout in seconds")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 