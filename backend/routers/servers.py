"""서버 관련 라우터"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import Server, Service, SvrGroup, Node, User, UserRole
from auth import get_current_active_user

router = APIRouter(prefix="/api", tags=["servers"])


@router.get("/servers")
async def get_all_servers(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """모든 서버 정보 반환 (검색 지원)"""
    query = db.query(Server)
    
    # 검색어가 있으면 필터링
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Server.name.ilike(search_filter)) |
            (Server.svg_name.ilike(search_filter))
        )
    
    servers = query.all()
    
    # role별로 다른 정보 제공
    user_role = current_user.role
    
    server_list = []
    for server in servers:
        # 기본 정보
        server_data = {
            "name": server.name,
            "svg": server.svg_name,
            "min": server.min_proc,
            "max": server.max_proc,
            "restart": server.restart
        }
        
        # 노드명 추가 (svg -> node 조회)
        svg = db.query(SvrGroup).filter(SvrGroup.name == server.svg_name).first()
        if svg:
            server_data["node"] = svg.node_name
        else:
            server_data["node"] = ""
        
        # infrastructure 이상 권한에 추가 정보
        if user_role in [UserRole.INFRASTRUCTURE, UserRole.ADMIN]:
            server_data.update({
                "maxqcount": server.maxqcount,
                "asqcount": server.asqcount,
                "db_info": server.db_info
            })
        
        server_list.append(server_data)
    
    return {
        "success": True,
        "servers": server_list,
        "total": len(server_list)
    }


@router.get("/server/{name}")
async def get_server_info(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """특정 서버 상세 정보"""
    server = db.query(Server).filter(Server.name == name).first()
    
    if not server:
        raise HTTPException(status_code=404, detail=f"Server '{name}' not found")
    
    # 해당 서버의 서비스(TR) 목록
    services = db.query(Service).filter(Service.server_name == name).all()
    
    # 노드명 찾기
    svg = db.query(SvrGroup).filter(SvrGroup.name == server.svg_name).first()
    node_name = svg.node_name if svg else ""
    
    # 기본 서버 상세 정보
    server_data = {
        "name": server.name,
        "svg_name": server.svg_name,
        "node_name": node_name,
        "min_proc": server.min_proc,
        "max_proc": server.max_proc,
        "restart": server.restart,
        "services": [{
            "name": s.name,
            "timeout": s.timeout,
            "autotran": s.autotran,
            "export": s.export
        } for s in services]
    }
    
    # infrastructure 이상 권한에 추가 정보
    if current_user.role in [UserRole.INFRASTRUCTURE, UserRole.ADMIN]:
        server_data.update({
            "maxqcount": server.maxqcount,
            "asqcount": server.asqcount,
            "db_info": server.db_info
        })
    
    return {
        "success": True,
        "server": server_data
    }
