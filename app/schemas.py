from pydantic import BaseModel

class Source(BaseModel):
    name: str
    url: str

class SourceOut(BaseModel):
    id: int
    name: str
    url: str