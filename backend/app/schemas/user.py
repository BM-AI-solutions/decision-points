from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to receive via API on update
class UserUpdate(BaseModel): # Don't inherit UserBase to allow partial updates easily
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None # Allow password update
    is_active: Optional[bool] = None

# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    # updated_at: Optional[datetime] # Often excluded from response models unless needed

    class Config:
        orm_mode = True # Pydantic V1 style, use from_attributes=True in V2

# Properties to return to client (doesn't include hashed_password)
class User(UserInDBBase):
    pass # Inherits all necessary fields from UserInDBBase

# Properties stored in DB (includes hashed_password)
class UserInDB(UserInDBBase):
    hashed_password: str

    class Config:
        orm_mode = True # Pydantic V1 style, use from_attributes=True in V2