from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User, UserLogin
from app.crud import user_crud
from app.auth import create_access_token,hash_password, verify_password
from app.utils.mongo import serialize_doc


router = APIRouter(prefix="/users", tags=["Users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

# --- Signup ---
@router.post("/signup", summary="Register a new user")
async def signup(form_data: User):
    existing_user = await user_crud.get_user_by_email(form_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # hash password using passlib
    hashed_pw = hash_password(form_data.password)

    user_dict = form_data.dict(exclude_unset=True)
    user_dict["password"] = hashed_pw

    await user_crud.create_user(user_dict)
    return {"msg": "User created successfully"}



# --- Login ---
@router.post("/login", summary="Login and get access token")
async def login(form_data: UserLogin):
    db_user = await user_crud.get_user_by_email(form_data.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # verify password with passlib
    if not verify_password(form_data.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token({"sub": str(db_user["_id"])})
    return {"access_token": token, "token_type": "bearer"}


# --- Get user ---
@router.get("/{user_id}", summary="Get a user by ID")
async def get_user(user_id: str):
    user = await user_crud.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return serialize_doc(user)
