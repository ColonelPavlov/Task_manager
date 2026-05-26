import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()


class Settings:

    DB_USER: str = os.getenv("DB_USER", "change_me")
    DB_PASS: str = os.getenv("DB_PASS", "change_me")
    DB_HOST: str = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_NAME: str = os.getenv("DB_NAME", "change_me")

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev_secret")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "dev_secret")

    @property
    def DATABASE_URL(self) -> str:
        safe_password = urllib.parse.quote_plus(self.DB_PASS)
        return f"mysql+aiomysql://{self.DB_USER}:{safe_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    

settings = Settings()