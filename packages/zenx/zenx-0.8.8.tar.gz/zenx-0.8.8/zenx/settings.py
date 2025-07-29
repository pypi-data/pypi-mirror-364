from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import find_dotenv


class Settings(BaseSettings):
    APP_ENV: str = "dev"

    SESSION_POOL_SIZE: int = 1
    MAX_SCRAPE_DELAY: int = 10  # 10 seconds
    DQ_MAX_SIZE: int = 100  # max size of the deque for memory database
    REDIS_RECORD_EXPIRY_SECONDS: int = 604800 # 7 days (7*24*60*60)

    DB_TYPE: Literal["memory", "redis"] = "memory"
    DB_NAME: str | None = None
    DB_USER: str | None = None
    DB_PASS: str | None = None
    DB_HOST: str | None = None
    DB_PORT: int | None = None
    
    PROXY_v4: str | None = None
    PROXY_V6: str | None = None
    
    GRPC_SERVER_URI: str = "ingress.opticfeeds.com"
    GRPC_TOKEN: str | None = None
    GRPC_ID: str | None = None
    GRPC_ID_HEADLINE: str | None = None

    SYNOPTIC_API_KEY: str | None = None
    SYNOPTIC_STREAM_ID: str | None = None

    model_config = SettingsConfigDict(env_file=find_dotenv(".env"))

settings = Settings()
