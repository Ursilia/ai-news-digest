from sqlalchemy.orm import Session
from app import models, security
from app.schemas import  SourceCreate, TagCreate, UserCreate
from app.repositories import SourceRepository,TagRepository, UserRepository
from app.exceptions import ConflictError, NotFoundError, BadRequestError as AppBadRequest, UnauthorizedError, LLMServiceError
from sqlalchemy.exc import IntegrityError

from openai import OpenAIError, AuthenticationError, BadRequestError, RateLimitError
from app.llm import summarizer, chat

from typing import AsyncGenerator


# Core functions

def create_source(db: Session, source: SourceCreate, owner_id: int) -> models.Source:
    repo = SourceRepository(db)
    url_str = str(source.url)
    if repo.get_by_url(url=url_str, owner_id=owner_id) is not None:
        raise ConflictError("You already have a source with this URL")
    try:
        return repo.create(name=source.name, url=url_str, owner_id=owner_id)
    except IntegrityError:
        raise ConflictError("You already have a source with this URL")


def get_all_sources(db: Session,owner_id:int, limit: int = 10, search: str | None = None) -> list[models.Source]:
    repo = SourceRepository(db)
    return repo.get_all(owner_id=owner_id, limit=limit, search=search)

def get_source(db: Session, source_id: int, owner_id: int) -> models.Source:
    repo = SourceRepository(db)
    source = repo.get_by_id(source_id=source_id, owner_id=owner_id)
    if source is None:
        raise NotFoundError("Source not found")
    return source

def update_source(db: Session, source_id: int, source: SourceCreate, owner_id: int) -> models.Source:
    repo = SourceRepository(db)
    existing = repo.get_by_id(source_id=source_id, owner_id=owner_id)
    if existing is None:
        raise NotFoundError("Source not found")
    try:
        return repo.update(existing, name=source.name, url=str(source.url))
    except IntegrityError:
        raise ConflictError("You already have a source with this URL")


def delete_source(db: Session, source_id: int, owner_id: int):
    repo = SourceRepository(db)
    existing = repo.get_by_id(source_id=source_id, owner_id=owner_id)
    if existing is None:
        raise NotFoundError("Source not found")
    repo.delete(existing)

# Tag functions

def create_tag(db: Session, tag: TagCreate) -> models.Tag:
    repo = TagRepository(db)
    if repo.get_by_name(name=tag.name) is not None:
        raise ConflictError("Tag with this name already exists")
    try:
        return repo.create(name=tag.name, description=tag.description)
    except IntegrityError:
        raise ConflictError("Tag with this name already exists")


def get_all_tags(db: Session, limit: int = 10, search: str | None = None) -> list[models.Tag]:
    repo = TagRepository(db)
    return repo.get_all(limit=limit, search=search)

def get_tag(db: Session, tag_id: int) -> models.Tag:
    repo = TagRepository(db)
    tag = repo.get_by_id(tag_id=tag_id)
    if tag is None:
        raise NotFoundError("Tag not found")
    return tag

def update_tag(db: Session, tag_id: int, tag: TagCreate) -> models.Tag:
    repo = TagRepository(db)
    existing = repo.get_by_id(tag_id=tag_id)
    if existing is None:
        raise NotFoundError("Tag not found")
    try:
        return repo.update(existing, name=tag.name, description=tag.description)
    except IntegrityError:
        raise NotFoundError("Tag not found")

def delete_tag(db: Session, tag_id: int):
    repo = TagRepository(db)
    existing = repo.get_by_id(tag_id=tag_id)
    if existing is None:
        raise NotFoundError("Tag not found")
    repo.delete(existing)


#User-related functions

def register_user(db: Session, user_data: UserCreate) -> models.User:
    repo = UserRepository(db)
    if repo.get_by_email(email=user_data.email) is not None:
       raise ConflictError("User with this email already exists")
    hashed = security.hash_password(user_data.password)
    try:
        return repo.create(email=user_data.email, hashed_password=hashed)
    except IntegrityError:
        raise ConflictError("User with this email already exists")

    # Token auth

def login_user(db: Session, email: str, password: str) -> str:
    repo = UserRepository(db)
    user = repo.get_by_email(email=email)
    if user is None or not security.verify_password(password, user.hashed_password):
        raise UnauthorizedError("Invalid email or password")
    return security.create_access_token(user_id=user.id)

#LLM

async def summarize_article(text: str) -> str:
    try:
        return await summarizer.summarize_text(text)
    except AuthenticationError:
        raise LLMServiceError("AI service is misconfigured")
    except RateLimitError:
        raise LLMServiceError("AI service is currently overloaded, please retry later")
    except BadRequestError:
        raise AppBadRequest("Text was rejecter by AI service")
    except OpenAIError:
        raise LLMServiceError()

async def ask_question(question: str, history: list) -> str:
    try:
        return await chat.ask_question(question=question, history=history)
    except AuthenticationError:
        raise LLMServiceError("AI service is misconfigured")
    except RateLimitError:
        raise LLMServiceError("AI service is currently overloaded, please retry later")
    except BadRequestError:
        raise AppBadRequest("Question was rejected by AI service")
    except OpenAIError:
        raise LLMServiceError()

async def ask_question_stream(
        question: str,
        history: list
) -> AsyncGenerator[str, None]:
    try:
        async for chunk in chat.ask_question_stream(question=question, history=history):
            yield chunk
    except AuthenticationError:
        raise LLMServiceError("AI service is misconfigured")
    except RateLimitError:
        raise LLMServiceError("AI service is currently overloaded, please retry later")
    except BadRequestError:
        raise AppBadRequest("Question was rejected by AI service")
    except OpenAIError:
        raise LLMServiceError()
