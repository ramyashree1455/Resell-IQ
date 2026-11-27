from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .security import decode_token

oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)) -> User:
    uid = decode_token(token)
    user = db.get(User, uid) if uid else None
    if not user:
        raise HTTPException(401, "Invalid or expired token")
    if user.role == "banned":
        raise HTTPException(403, "This account has been banned")
    return user


def require_roles(*roles):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(403, "You do not have permission")
        return user
    return checker
