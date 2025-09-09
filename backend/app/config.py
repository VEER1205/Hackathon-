from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Optional with default values
    MONGO_URI: str = "mongodb://localhost:27017"
    DB_NAME: str = "mydatabase"

    # Required (no defaults)
    API_KEY: str
    SECRET_KEY: str
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    session_secret: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
print("DEBUG SETTINGS:", settings.model_dump())
