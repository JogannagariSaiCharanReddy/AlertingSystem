from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    DB_URL: str

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }


settings = Settings()