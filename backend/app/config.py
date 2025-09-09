from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    MONGO_URI: str
    DB_NAME: str
    API_KEY: str = os.getenv("API_KEY")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = os.getenv("GOOGLE_REDIRECT_URI")
    session_secret: str = os.getenv("SESSION_SECRET")

    class Config:
        env_file = ".env"   # looks for backend/.env
        env_file_encoding = "utf-8"

settings = Settings()
print("DEBUG:", settings.model_dump())  