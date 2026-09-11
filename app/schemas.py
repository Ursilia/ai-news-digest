from pydantic import BaseModel, HttpUrl, EmailStr, Field
from datetime import datetime

class SourceCreate(BaseModel):
    name: str
    url: HttpUrl

class SourceOut(BaseModel):
    id: int
    name: str
    url: str
    owner_id: int
    created_at: datetime

    model_config = {"from_attributes": True}

class TagCreate(BaseModel):
    name: str
    description: str | None = None

class TagOut(BaseModel):
    id: int
    name: str
    description: str | None

    model_config = {"from_attributes": True}

class UserCreate(BaseModel):
    email : EmailStr
    password: str = Field(min_length=8, max_length=100)

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes":True}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

