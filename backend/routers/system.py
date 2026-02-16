"""시스템 관련 라우터 (헬스체크, 리로드 등)"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from auth import get_current_active_user
from models import User, UserRole

router = APIRouter(prefix="/api", tags=["system"])

# 마지막 업데이트 시간
last_update = datetime.utcnow()


@router.get("/reload")
async def reload_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """설정 파일 재로드 (ADMIN 또는 INFRASTRUCTURE만)"""
    global last_update
    
    if current_user.role not in [UserRole.ADMIN, UserRole.INFRASTRUCTURE]:
        raise HTTPException(
            status_code=403,
            detail="권한이 없습니다. ADMIN 또는 INFRASTRUCTURE 권한이 필요합니다."
        )
    
    try:
        # main 모듈의 load_all_configs_to_db 함수 import
        from main import load_all_configs_to_db
        
        # DB 재로드
        load_all_configs_to_db(db)
        
        # 마지막 업데이트 시간 갱신
        last_update = datetime.utcnow()
        
        return {
            "success": True,
            "message": "Configuration reloaded successfully",
            "timestamp": last_update.isoformat(),
            "reloaded_by": current_user.username
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Config reload failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "TPOps Backend API",
        "version": "2.0.0"
    }


def get_last_update() -> datetime:
    """마지막 업데이트 시간 반환"""
    return last_update
