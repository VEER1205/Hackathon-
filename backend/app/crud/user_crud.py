from app.database import db
from app.utils.mongo import to_object_id

collection = db["users"]

async def create_user(user_dict: dict) -> str:
    # remove optional id if present
    user_dict.pop("id", None)
    result = await collection.insert_one(user_dict)
    return str(result.inserted_id)

async def get_user(user_id: str):
    return await collection.find_one({"_id": to_object_id(user_id)})

async def list_users(limit: int = 100):
    return await collection.find().limit(limit).to_list(length=limit)

async def update_user(user_id: str, data: dict) -> bool:
    data.pop("id", None)
    res = await collection.update_one({"_id": to_object_id(user_id)}, {"$set": data})
    return res.modified_count > 0

async def delete_user(user_id: str) -> bool:
    res = await collection.delete_one({"_id": to_object_id(user_id)})
    return res.deleted_count > 0
