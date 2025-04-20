from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

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

    # Database configuration (placeholder)
    DATABASE_URL: str = "postgresql+asyncpg://user:password@host:port/db"

    # Kafka configuration (placeholder)
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_EXAMPLE_TOPIC: str = "example_topic"
    KAFKA_CONSUMER_GROUP_ID: str = "decision_points_group"
    LOG_LEVEL: str = "INFO" # Default log level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)

    # Uvicorn settings (if running directly)
    UVICORN_HOST: str = "0.0.0.0"
    UVICORN_PORT: int = 8000
    UVICORN_RELOAD: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache()
def get_settings() -> Settings:
    """Returns the settings instance, cached for performance."""
    return Settings()

settings = get_settings()