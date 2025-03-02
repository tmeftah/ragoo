# User routes (API endpoints)
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ragoo.database.database import get_db
from ragoo.schemas.user import UserCreate, UserResponse, Token
from ragoo.services.user_service import create_user, get_user_by_username
from ragoo.core.security import create_access_token, verify_password

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db, user)


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  # <-- Use OAuth2 form
    db: Session = Depends(get_db),
):
    user = get_user_by_username(db, form_data.username)  # <-- Access via form_data
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
