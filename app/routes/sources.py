from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import SourceCreate, SourceOut
from app import services, models

router = APIRouter(prefix="/sources", tags=["sources"])

@router.post("", status_code=201, response_model=SourceOut)
async def create_source(
    source: SourceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return services.create_source(db=db, source=source, owner_id=current_user.id)

@router.get("", response_model=list[SourceOut])
async def get_all_sources(limit: int = 10, 
                          search: str | None = None, 
                          db: Session = Depends(get_db),
                          current_user: models.User = Depends(get_current_user),
                          ):
    return services.get_all_sources(db=db, owner_id=current_user.id, search=search, limit=limit)

@router.get("/{source_id}", response_model=SourceOut)
async def get_sources(source_id: int, 
                      db: Session = Depends(get_db),
                      current_user: models.User = Depends(get_current_user), 
                      ):
    return services.get_source(db=db, source_id=source_id, owner_id=current_user.id)


@router.put("/{source_id}", response_model=SourceOut)
async def update_source(source_id: int, 
                        source: SourceCreate, 
                        db: Session = Depends(get_db),
                        current_user: models.User = Depends(get_current_user),):
    return services.update_source(db=db, source_id=source_id, source=source, owner_id=current_user.id)

@router.delete("/{source_id}", status_code=204)
async def delete_source(source_id: int, 
                        db: Session = Depends(get_db), 
                        current_user: models.User = Depends(get_current_user)):
    return services.delete_source(db=db, source_id=source_id, owner_id=current_user.id)


