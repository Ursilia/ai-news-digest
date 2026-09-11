from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import TagCreate, TagOut
from app import services, models

router = APIRouter(tags=["tags"], prefix="/tags")


@router.post("", status_code=201, response_model=TagOut)
async def create_tag(tag: TagCreate, 
                     db: Session = Depends(get_db),
                     current_user: models.User = Depends(get_current_user),):
    return services.create_tag(db=db, tag=tag)

@router.get("", response_model=list[TagOut])
async def get_all_tags(limit: int = 10,
                       search: str | None = None,
                       db: Session = Depends(get_db),
                       current_user: models.User = Depends(get_current_user),):
    return services.get_all_tags(db=db, limit=limit, search=search)

@router.get("/{tag_id}", response_model=TagOut)
async def get_tag(
    tag_id= int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return services.get_tag(db=db, tag_id=tag_id)

@router.put("/{tag_id}", response_model=TagOut)
async def update_tag(
    tag_id: int, 
    tag: TagCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return services.update_tag(db=db, tag_id=tag_id, tag=tag)

@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return services.delete_tag(db=db, tag_id=tag_id)

