from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app import crud, auth, models
from app.database import get_db

security = HTTPBearer(auto_error=False)


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[models.User]:
    if credentials is None:
        return None
    token = credentials.credentials
    payload = auth.decode_access_token(token)
    if payload is None:
        return None
    username = payload.get("sub")
    if username is None:
        return None
    user = crud.get_user_by_username(db, username)
    return user


def get_current_user_required(
    current_user: Optional[models.User] = Depends(get_current_user_optional),
) -> models.User:
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return current_user


def require_admin(
    current_user: models.User = Depends(get_current_user_required),
) -> models.User:
    if current_user.group != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user
