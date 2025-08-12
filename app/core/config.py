from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Sistema Vendas"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API para Sistema de Controle de Pedidos, Estoque e Finanças"

    # Database Settings
    DATABASE_URL: str = "mysql+pymysql://vendas_user:vendas_pass@localhost:3306/vendas_ceasa"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 3306
    DATABASE_USER: Optional[str] = "vendas_user"
    DATABASE_PASSWORD: Optional[str] = "vendas_pass"
    DATABASE_NAME: Optional[str] = "vendas_ceasa"
    
    # Security Settings
    SECRET_KEY: str = "desenvolvimento_chave_secreta_123"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Upload Settings
    UPLOAD_FOLDER: str = "uploads"
    MAX_FILE_SIZE: int = 5242880  # 5MB
    
    # Google Drive Settings
    RCLONE_CONFIG_PATH: str = "/app/rclone.conf"
    GDRIVE_REMOTE_NAME: str = "gdrive"
    GDRIVE_FOLDER_ID: str = ""
    
    # Development Settings
    DEBUG: bool = True
    TESTING: bool = False
    LOG_LEVEL: str = "INFO"
    
    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:5174"
    ]
    
    # Timezone Settings
    TIMEZONE: str = "America/Sao_Paulo"

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"  # Allow extra environment variables
    }


settings = Settings()
