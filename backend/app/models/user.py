from pydantic import BaseModel, EmailStr
from typing import List, Optional

class User(BaseModel):
    id: Optional[str] = None
    name: str
    email: EmailStr
    skills: List[str] = []
    interests: List[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "skills": ["Python", "Data Science"],
                "interests": ["AI", "ML"]
            }
        }
