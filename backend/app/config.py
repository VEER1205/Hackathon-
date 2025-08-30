from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    DB_NAME: str

    class Config:
        env_file = ".env"   # looks for backend/.env
        env_file_encoding = "utf-8"

settings = Settings()
print("DEBUG:", settings.model_dump())  