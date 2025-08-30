from pydantic import BaseModel, EmailStr
from typing import List, Optional

class User(BaseModel):
    id: Optional[str] = None
    name: str
    email: EmailStr
    skills: List[str] = []
    interests: List[str] = []
