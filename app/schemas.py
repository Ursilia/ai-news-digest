from pydantic import BaseModel, HttpUrl

class SourceCreate(BaseModel):
    name: str
    url: HttpUrl

class SourceOut(BaseModel):
    id: int
    name: str
    url: str

    model_config = {"from_attributes": True}

class TagCreate(BaseModel):
    name: str
    description: str | None = None

class TagOut(BaseModel):
    id: int
    name: str
    description: str | None

    model_config = {"from_attributes": True}
