from app.database import db
from app.models import user
from app.utils.mongo import to_object_id
from app.auth import hash_password

collection = db["users"]

# --- Create User ---
async def create_user(user_dict: dict) -> str:
    """Insert a new user into MongoDB."""
    user_data = user_dict

    if "password" not in user_data:
        raise ValueError("Missing password in user data")

    user_data["password"] = hash_password(user_data["password"])
    result = await collection.insert_one(user_data)
    return str(result.inserted_id)

# --- add password if user have account but not password ---
async def add_password_if_missing(email: str, password: str) -> bool:
    """Add a password to an existing user if it doesn't have one."""
    result = await collection.update_one(
        {"email": email, "password": None},
        {"$set": {"password": hash_password(password)}}
    )
    return result.modified_count > 0

# --- Get User by Email ---
async def get_user_by_email(email: str) -> dict:
    """Find a user by email."""
    return await collection.find_one({"email": email})

# --- Get User by ID ---
async def get_user(user_id: str) -> dict | None:
    """Find a user by ID."""
    return await collection.find_one({"_id": to_object_id(user_id)})

# --- Update User ---
async def update_user(user_id: str, data: dict) -> bool:
    """Update user details."""
    data.pop("id", None)  # remove id if passed
    res = await collection.update_one(
        {"_id": to_object_id(user_id)},
        {"$set": data}
    )
    return res.modified_count > 0

# --- Delete User ---
async def delete_user(user_id: str) -> bool:
    """Delete user by ID."""
    res = await collection.delete_one({"_id": to_object_id(user_id)})
    return res.deleted_count > 0


 # whatever your MongoDB connection is
async def get_or_create_user(user_data: dict):
    collection = db["users"]
    existing_user = await collection.find_one({"email": user_data["email"]})

    if existing_user:
        return existing_user

    result = await collection.insert_one(user_data)
    return await collection.find_one({"_id": result.inserted_id})

