from fastapi import Depends, Request
from sqlalchemy.orm import Session
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from fastapi.security import OAuth2PasswordBearer

from app.database import get_db
from app import security, models
from app.repositories import UserRepository
from app.exceptions import UnauthorizedError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    try:
        payload = security.decode_access_token(token)
    except ExpiredSignatureError:
        raise UnauthorizedError("Token has expired")
    except InvalidTokenError:
        raise UnauthorizedError("Invalid token")

    user_id_raw = payload.get("sub")
    if user_id_raw is None:
        raise UnauthorizedError("Invalid token payload")
    try:
        user_id = int(user_id_raw)
    except ValueError:
        raise UnauthorizedError("Invalid token payload")

    repo = UserRepository(db)
    user = repo.get_by_id(used_id=user_id)
    if user is None:
        raise UnauthorizedError("User not found")

    return user