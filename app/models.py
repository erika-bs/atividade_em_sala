from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict

class UserIn(BaseModel):
    name: str = Field(min_length=2,max_length=50)
    email: EmailStr
    age: int = Field(ge=0)
    is_active: bool = True

class UserUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    age: Optional[int]
    is_active: Optional[bool]

class UserOut(BaseModel):
    id: str
    name: str 
    email: EmailStr
    age: int
    is_active: bool

    model_config = ConfigDict(populate_by_name=True)