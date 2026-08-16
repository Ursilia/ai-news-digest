from fastapi import APIRouter, HTTPException
from app.schemas import Source, SourceOut
from app import services

router = APIRouter()

@router.post("/sources", status_code=201, response_model=SourceOut)
async def create_source(source: Source):
    return services.create_source(source)

@router.get("/sources", response_model=list[SourceOut])
async def get_all_sources(limit: int = 10, search: str | None = None):
    return services.get_all_sources(limit=limit, search=search)

@router.get("/sources/{source_id}", response_model=SourceOut)
async def get_source(source_id: int):
    source = services.get_source(source_id)
    if source is None:
        HTTPException(status_code=404, detail="Source not found")
    return source

@router.put("/sources/{source_id}", response_model=SourceOut)
async def update_source(source_id: int, source: Source):
    updated = services.update_source(source_id=source_id, source=source)
    if updated is None:
        HTTPException(status_code=404, detail="Source not found")
    return updated

@router.delete("/sources/{source_id}", status_code=204)
async def delete_source(source_id: int):
    if not services.delete_source(source_id):
        raise HTTPException(status_code=404, detail="Source not found")