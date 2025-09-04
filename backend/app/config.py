from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    MONGO_URI: str
    DB_NAME: str
    API_KEY: str = os.getenv("API_KEY")

    class Config:
        env_file = ".env"   # looks for backend/.env
        env_file_encoding = "utf-8"

settings = Settings()
print("DEBUG:", settings.model_dump())  