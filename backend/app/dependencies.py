from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
import crud
import models
from security import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
  token: str = Depends(oauth2_scheme),
  db: Session = Depends(get_db)
):
  payload = decode_access_token(token)

  if payload is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid token"
    )

  username: str = payload.get("sub")

  if username is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid token"
    )

  user = crud.get_user_by_username(db, username=username)

  if user is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="User not found"
    )

  return user


def get_current_admin_user(
  current_user: models.User = Depends(get_current_user)
):
  if not current_user.is_admin:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="Not an admin"
    )

  return current_user