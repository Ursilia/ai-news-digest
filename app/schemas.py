from pydantic import BaseModel, HttpUrl, EmailStr, Field
from datetime import datetime
from typing import Literal


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

class SummarizeRequest(BaseModel):
    text: str = Field(min_length=50, max_length=50000)

class SummarizeResponse(BaseModel):
    summary: str


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=10000)

class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)

class AskResponse(BaseModel):
    answer: str



class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=50, max_length=200000)

class DocumentOut(BaseModel):
    id: int
    title: str
    created_at: datetime
    owner_id: int

    model_config={"from_attributes": True}

class DocumentWithChunksCount(DocumentOut):
    chunks_count: int


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    limit: int = Field(default=5, ge=1, le=20)

class ChunkSearchResult(BaseModel):
    content: str
    distance: float
    document_id: int
    chunk_index: int

class SearchResponse(BaseModel):
    query: str
    results: list[ChunkSearchResult]

class RAGRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=10)

class RAGSource(BaseModel):
    document_id: int
    chunk_index: int
    content: str
    distance: float

class RAGResponse(BaseModel):
    question: str
    answer: str
    sources: list[RAGSource]
