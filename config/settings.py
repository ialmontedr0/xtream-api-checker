from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    BOT_TOKEN: str
    DEBUG: bool = True
    REQUEST_TIMEOUT: int = 15
    RATE_LIMIT: int = 5

    # Batch
    MAX_BATCH_SIZE: int = 100
    BATCH_DELAY: float = 1.0

settings = Settings()
