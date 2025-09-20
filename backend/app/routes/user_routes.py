from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from app.models.user import User, UserLogin
from app.crud import user_crud
from app.auth import create_access_token, hash_password, verify_password
from app.utils.mongo import serialize_doc
from app.routes.auth_routes import create_access_token, verify_token

router = APIRouter(prefix="/users", tags=["Users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

# --- Signup ---
@router.post("/signup", summary="Register a new user")
async def signup(form_data: User):
    existing_user = await user_crud.get_user_by_email(form_data.email)
    if existing_user and not existing_user.get("password", None) is None:
        raise HTTPException(status_code=400, detail="User already exists")

    if existing_user.get("password", None) is None:
        await user_crud.add_password_if_missing(form_data.email, form_data.password)
        return {"msg": "Password added to existing user"}
    user_dict = form_data.dict(exclude_unset=True)
    
    await user_crud.create_user(user_dict)
    return {"msg": "User created successfully"}

# --- Login ---
@router.post("/login", summary="Login and get access token")
async def login(form_data: UserLogin):
    db_user = await user_crud.get_user_by_email(form_data.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not db_user.get("password", None):
        raise HTTPException(status_code=400, detail="User has no password set. or Please use Google login.")
    # Verify the password
    if not verify_password(form_data.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect password")

    # Create JWT token
    access_token = create_access_token(data={"sub": form_data.email})

    # Set HttpOnly cookie and redirect to frontend
    response = RedirectResponse(url="https://futuro-ai.web.app")
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="None",  # Change this to allow cross-site requests
        
    )
    return response

# --- Get User ---
@router.get("/{user_id}", summary="Get a user by ID")
async def get_user(user_id: str):
    user = await user_crud.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return serialize_doc(user)
