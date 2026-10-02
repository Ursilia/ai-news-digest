from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import DocumentCreate, DocumentOut, SearchRequest, SearchResponse, RAGRequest, RAGResponse
from app import services, models

from app.repositories import DocumentRepository
from app.exceptions import NotFoundError


router = APIRouter(tags=["/documents"], prefix="/documents")

@router.post("", response_model=DocumentOut, status_code=201)
async def upload_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return await services.upload_document(
        db=db,
        title=document.title,
        content=document.content,
        owner_id=current_user.id,
    )

@router.get("", response_model=list[DocumentOut])
async def list_documents(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return services.list_documents(db=db, owner_id=current_user.id, limit=limit)

@router.get("/{document_id}", response_model=DocumentOut)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return services.get_document(db=db, owner_id=current_user.id, document_id=document_id)

@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return services.delete_document(db=db, document_id=document_id, owner_id=current_user.id)


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return await services.search_documents(
        db=db,
        query=request.query,
        owner_id=current_user.id,
        limit=request.limit,
    )

@router.post("/ask", response_model=RAGResponse)
async def rag_ask(
    request: RAGRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return await services.rag_answer(
        db=db,
        question=request.question,
        owner_id=current_user.id,
        top_k=request.top_k,
    )
