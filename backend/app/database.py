from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

# Motor auto-enables TLS for mongodb+srv URIs.
client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.DB_NAME]
