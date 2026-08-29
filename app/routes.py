from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas import SourceCreate, SourceOut, TagCreate, TagOut
from app.database import get_db
from app import services

router = APIRouter()

@router.post("/sources", status_code=201, response_model=SourceOut)
async def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    return services.create_source(source=source, db=db)

@router.get("/sources", response_model=list[SourceOut])
async def get_all_sources(limit: int = 10, 
                          search: str | None = None,
                          db: Session = Depends(get_db)):
    return services.get_all_sources(db=db, limit=limit, search=search)

@router.get("/sources/{source_id}", response_model=SourceOut)
async def get_source(source_id: int, db:Session = Depends(get_db)):
    return services.get_source(db=db, source_id=source_id)

@router.put("/sources/{source_id}", response_model=SourceOut)
async def update_source(source_id: int, source: SourceCreate, db:Session = Depends(get_db)):
    return services.update_source(db=db, source_id=source_id, source=source)

@router.delete("/sources/{source_id}", status_code=204)
async def delete_source(source_id: int, db: Session = Depends(get_db)):
    return services.delete_source(source_id=source_id, db=db)

# Tag routes

@router.post("/tags", status_code=201, response_model=TagOut)
async def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    return services.create_tag(db=db, tag=tag)

@router.get("/tags", response_model=list[TagOut])
async def get_all_tags(limit: int = 10, search: str | None = None, db: Session = Depends(get_db)):
    return services.get_all_tags(db=db, limit=limit, search=search)

@router.get("/tags/{tag_id}", response_model=TagOut)
async def get_tag(tag_id: int, db: Session = Depends(get_db)):
    return services.get_tag(db=db, tag_id=tag_id)

@router.delete("/tags/{tag_id}", status_code=204)
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    return services.delete_tag(db=db, tag_id=tag_id)
    