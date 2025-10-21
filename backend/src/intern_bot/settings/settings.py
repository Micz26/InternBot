from pydantic_settings import BaseSettings
from pydantic import SecretStr

class Settings(BaseSettings):
    OPENAI_API_KEY: SecretStr

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: SecretStr

    OFFERS_TABLE_NAME: str = 'offers'

    # Server configuration
    SERVER_IP: str
    FRONTEND_PORT: str

    # LangSmith tracing
    LANGSMITH_TRACING: bool = False
    LANGSMITH_ENDPOINT: str | None = None
    LANGSMITH_API_KEY: SecretStr | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
