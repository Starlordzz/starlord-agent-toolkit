"""
Server configuration module.
Loads settings from environment variables or command-line arguments.
"""
import os
from typing import Optional
from pydantic import BaseModel, Field


class Settings(BaseModel):
    # Server network settings
    host: str = Field(default=os.getenv("AUTOMATION_HOST", "127.0.0.1"))
    port: int = Field(default=int(os.getenv("AUTOMATION_PORT", "8765")))

    # Idle auto-shutdown in seconds (0 means never shutdown)
    idle_timeout: int = Field(default=int(os.getenv("AUTOMATION_IDLE_TIMEOUT", "60")))

    # Default Android device serial (optional)
    default_serial: Optional[str] = Field(default=os.getenv("ANDROID_SERIAL", None))

    # AI / LLM Configuration
    llm_api_key: Optional[str] = Field(
        default=os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY", None)
    )
    llm_base_url: Optional[str] = Field(
        default=os.getenv("OPENAI_BASE_URL") or os.getenv("LLM_BASE_URL", None)
    )
    llm_model: str = Field(
        default=os.getenv("LLM_MODEL", "gpt-4o-mini")
    )


settings = Settings()

