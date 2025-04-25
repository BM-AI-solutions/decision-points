from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    """
    PROJECT_NAME: str = "Decision Points Backend"
    API_V1_STR: str = "/api/v1"

    # JWT settings
    SECRET_KEY: str = "a_very_secret_key_that_should_be_in_env" # TODO: Generate a strong key and move to .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # Default to 30 minutes

    # Database configuration
    DATABASE_URL: str = "postgresql+asyncpg://user:password@host:port/db"

    # Kafka configuration
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_EXAMPLE_TOPIC: str = "example_topic"
    KAFKA_CONSUMER_GROUP_ID: str = "decision_points_group"

    # Logging
    LOG_LEVEL: str = "INFO" # Default log level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)

    # Uvicorn settings (if running directly)
    UVICORN_HOST: str = "0.0.0.0"
    UVICORN_PORT: int = 8000
    UVICORN_RELOAD: bool = False

    # Agent & External API Keys / Configs
    GEMINI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None # For Google Search, etc.
    FIRECRAWL_API_KEY: Optional[str] = None
    EXA_API_KEY: Optional[str] = None
    PERPLEXITY_API_KEY: Optional[str] = None
    BRAVE_API_KEY: Optional[str] = None
    COMPOSIO_API_KEY: Optional[str] = None

    # Agent Operational Parameters
    AGENT_TIMEOUT_SECONDS: int = 300 # Timeout for A2A calls
    A2A_MAX_RETRIES: int = 3 # Max retries for A2A calls
    A2A_RETRY_DELAY_SECONDS: int = 2 # Delay between retries

    # Agent Specific Configs
    COMPETITOR_SEARCH_PROVIDER: str = "exa" # Default search provider
    GEMINI_MODEL_NAME: str = "gemini-2.5-flash-preview-04-17" # Default model

    # Agent Service Locators (URLs/IDs - Phase 1 might use IDs, Phase 2 URLs/Discovery)
    # Using Optional[str] as they might not be set in all envs or needed by all parts
    AGENT_WEB_SEARCH_ID: Optional[str] = "agent-web-search" # Default ID for the web search agent service
    AGENT_WEB_SEARCH_URL: Optional[str] = None
    CONTENT_GENERATION_AGENT_ID: Optional[str] = None
    CONTENT_GENERATION_AGENT_URL: Optional[str] = None
    # Add other agent IDs/URLs as needed

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache()
def get_settings() -> Settings:
    """Returns the settings instance, cached for performance."""
    return Settings()

settings = get_settings()