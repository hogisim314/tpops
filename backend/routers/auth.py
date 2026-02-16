"""인증 관련 라우터"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from database import get_db
from models import User, UserRole
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_active_user,
    require_role,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """로그인"""
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, str(user.hashed_password)):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    if not getattr(user, 'is_active', True):
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # 마지막 로그인 시간 업데이트
    setattr(user, 'last_login', datetime.utcnow())
    db.commit()
    
    # JWT 토큰 생성
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value
        }
    }


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """현재 로그인한 사용자 정보"""
    return {
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
        "created_at": getattr(current_user.created_at, 'isoformat', lambda: None)(),
        "last_login": getattr(current_user.last_login, 'isoformat', lambda: None)()
    }


@router.post("/register")
async def register(
    username: str,
    password: str,
    email: str,
    full_name: str,
    role: UserRole = UserRole.DEVELOPER,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """새 사용자 등록 (관리자만 가능)"""
    # 중복 체크
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # 새 사용자 생성
    new_user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        role=role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "User created successfully",
        "user": {
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role.value
        }
    }
