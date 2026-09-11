from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import UserCreate, UserOut, TokenResponse
from app import services, models

router = APIRouter(tags=["auth"])

@router.post("/register", status_code=201, response_model=UserOut)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    return services.register_user(user_data=user_data, db=db)

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db),):
    access_token = services.login_user(db=db,email=form_data.username,password=form_data.password,)
    return TokenResponse(access_token=access_token)

@router.get("/me", response_model=UserOut)
async def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user