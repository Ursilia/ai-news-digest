from sqlalchemy.orm import Session
from app import models, security
from app.schemas import  SourceCreate, TagCreate, UserCreate, ChunkSearchResult, SearchResponse, RAGSource, RAGRequest, RAGResponse
from app.repositories import SourceRepository,TagRepository, UserRepository, DocumentRepository
from app.exceptions import ConflictError, NotFoundError, BadRequestError as AppBadRequest, UnauthorizedError, LLMServiceError
from sqlalchemy.exc import IntegrityError

from openai import OpenAIError, AuthenticationError, BadRequestError, RateLimitError
from app.llm import summarizer, chat

from typing import AsyncGenerator

from app.llm import chunker, embedder, rag


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

#LLM text

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

#Embedding 

async def upload_document(
        db: Session,
        title: str,
        content: str,
        owner_id: int,
) -> models.Document:
    try:
        chunk_texts = chunker.chunk_text(text=content)
        if not chunk_texts:
            raise AppBadRequest("Document produced no chunks")
        embeddings = await embedder.embed_texts(chunk_texts)
    except AuthenticationError:
        raise LLMServiceError("AI service is misconfigured")
    except RateLimitError:
        raise LLMServiceError("AI service is currently overloaded, please try later")
    except OpenAIError:
        raise LLMServiceError()

    repo = DocumentRepository(db)
    document = repo.create(title=title, content=content, owner_id=owner_id)

    chunks_data = list(zip(chunk_texts, embeddings))
    repo.add_chunks(document_id=document.id, chunks=chunks_data)

    return document

def list_documents(db: Session, owner_id: int, limit: int = 5):
    repo = DocumentRepository(db)
    return repo.get_all(owner_id=owner_id, limit=limit)

def get_document(db: Session, owner_id: int, document_id: int):
    repo = DocumentRepository(db)
    document = repo.get_by_id(document_id=document_id, owner_id=owner_id)
    if document is None:
        raise NotFoundError("Document with this id wasn't found")
    return document

def delete_document(db: Session, document_id: int, owner_id: int):
    repo = DocumentRepository(db)
    existing = repo.get_by_id(document_id=document_id, owner_id=owner_id)
    if existing is None:
        raise NotFoundError("Document with this id wasn't found")
    return repo.delete(existing)

async def search_documents(
        db:Session,
        query: str,
        owner_id: int,
        limit: int = 5,
) -> SearchResponse:
    try:
        query_embeddings = await embedder.embed_texts([query])
        query_embedding = query_embeddings[0]
    except AuthenticationError:
        raise LLMServiceError("AI service is misconfigured")
    except RateLimitError:
        raise LLMServiceError("AI service is currently overloaded, please retry later")
    except OpenAIError:
        raise LLMServiceError()

    repo = DocumentRepository(db)
    raw_results = repo.search_chunks(
        query_embedding=query_embedding,
        owner_id=owner_id,
        limit=limit,
    )

    results = [
        ChunkSearchResult(
            content=chunk.content,
            distance=float(distance),
            document_id=chunk.document_id,
            chunk_index=chunk.chunk_index,
        )
    for chunk, distance in raw_results
    ]

    return SearchResponse(query=query, results=results)

DISTANCE_THRESHOLD = 0.7

async def rag_answer(
        db: Session,
        question: str,
        owner_id: int,
        top_k: int = 5,
) -> RAGResponse:
    try:
        query_embeddings = await embedder.embed_texts([question])
        query_embedding = query_embeddings[0]
    except AuthenticationError:
        raise LLMServiceError("AI service is misconfigured")
    except RateLimitError:
        raise LLMServiceError("AI service is currently overloaded, please retry later")
    except OpenAIError:
        raise LLMServiceError()
    
    repo = DocumentRepository(db)
    raw_results = repo.search_chunks(
        query_embedding=query_embedding,
        owner_id=owner_id,
        limit=top_k,
    )

    relevant = [(chunk, distance) for chunk, distance in raw_results if distance < DISTANCE_THRESHOLD]

    if not relevant:
        return RAGResponse(
            question=question,
            answer="I cannot find this information in your documents",
            sources=[],
        )
    chunk_texts = [chunk.content for chunk, _ in relevant]

    try:
        answer = await rag.answer_with_context(question=question, chunks=chunk_texts)
    except AuthenticationError:
        raise LLMServiceError("AI service is misconfigured")
    except RateLimitError:
        raise LLMServiceError("AI service is currently overloaded, please retry later")
    except OpenAIError:
        raise LLMServiceError()

    sources = [
        RAGSource(
            document_id=chunk.document_id,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            distance=float(distance),
        )
        for chunk, distance in relevant
    ]
    
    return RAGResponse(
        question=question,
        answer=answer,
        sources=sources,
    )