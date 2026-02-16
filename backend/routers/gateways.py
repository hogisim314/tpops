"""게이트웨이 관련 라우터"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Gateway

router = APIRouter(prefix="/api", tags=["gateways"])


@router.get("/gateways")
async def get_all_gateways(db: Session = Depends(get_db)):
    """모든 게이트웨이 정보 반환"""
    gateways = db.query(Gateway).all()
    
    gateway_list = [{
        "name": g.name,
        "node": g.node_name,
        "port": g.port,
        "remote_addr": g.remote_addr,
        "remote_port": g.remote_port,
        "direction": g.direction,
        "gw_type": g.gw_type,
        "backup_addr": g.backup_addr,
        "backup_port": g.backup_port,
        "backup_rgwaddr": g.backup_rgwaddr,
        "backup_rgwportno": g.backup_rgwportno,
        "cpc": g.cpc,
        "restart": g.restart,
        "clopt": g.clopt
    } for g in gateways]
    
    return {
        "success": True,
        "gateways": gateway_list,
        "total": len(gateway_list)
    }
