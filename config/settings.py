from pydantic import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    DEBUG: bool = True
    
    # HTTP
    REQUEST_TIMEOUT: int = 10
    
    # Seguridad
    RATE_LIMIT: int = 5 # Solicitudes por usuario
    
    class Config:
        env_file = ".env"
        
settings = Settings()