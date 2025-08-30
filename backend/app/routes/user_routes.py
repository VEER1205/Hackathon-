from fastapi import APIRouter, HTTPException
from app.models.user import User
from app.crud import user_crud
from app.utils.mongo import serialize_doc, serialize_list

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", summary="Create a user")
async def create_user(user: User):
    user_id = await user_crud.create_user(user.dict(exclude_unset=True))
    return {"id": user_id}

@router.get("/{user_id}", summary="Get a user by ID")
async def get_user(user_id: str):
    user = await user_crud.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return serialize_doc(user)

@router.get("/", summary="List users")
async def list_users(limit: int = 100):
    users = await user_crud.list_users(limit)
    return serialize_list(users)

@router.put("/{user_id}", summary="Update user")
async def update_user(user_id: str, user: User):
    ok = await user_crud.update_user(user_id, user.dict(exclude_unset=True))
    if not ok:
        raise HTTPException(status_code=404, detail="User not found or no changes")
    return {"message": "User updated"}

@router.delete("/{user_id}", summary="Delete user")
async def delete_user(user_id: str):
    ok = await user_crud.delete_user(user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}
