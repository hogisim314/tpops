"""사용자 관리 관련 라우터 (Admin only)"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User, UserRole
from auth import require_role

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("")
async def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """모든 사용자 목록 (관리자만)"""
    users = db.query(User).all()
    
    return {
        "success": True,
        "users": [{
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role.value,
            "is_active": u.is_active,
            "created_at": getattr(u.created_at, 'isoformat', lambda: None)(),
            "last_login": getattr(u.last_login, 'isoformat', lambda: None)()
        } for u in users],
        "total": len(users)
    }


@router.put("/{user_id}/role")
async def update_user_role(
    user_id: int,
    new_role: UserRole,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """사용자 역할 변경 (관리자만)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    old_role = user.role
    setattr(user, 'role', new_role)
    db.commit()
    
    return {
        "success": True,
        "message": f"User role updated from {old_role.value} to {new_role.value}",
        "user": {
            "username": user.username,
            "role": user.role.value
        }
    }


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """사용자 삭제 (관리자만)"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    username = user.username
    db.delete(user)
    db.commit()
    
    return {
        "success": True,
        "message": f"User {username} deleted successfully"
    }
