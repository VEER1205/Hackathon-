from pydantic import BaseModel, EmailStr
from typing import List, Optional


class User(BaseModel):  # maps MongoDB _id
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str