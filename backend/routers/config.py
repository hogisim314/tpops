"""설정, 노드, 서버그룹 관련 라우터"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Domain, Node, SvrGroup, Server, Service, Gateway, User
from auth import get_current_active_user
from routers import system

router = APIRouter(prefix="/api", tags=["config"])


@router.get("/config")
async def get_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """설정 요약 정보 반환 (모든 로그인 사용자)"""
    nodes = db.query(Node).all()
    svrgroups = db.query(SvrGroup).all()
    servers = db.query(Server).all()
    services = db.query(Service).all()
    gateways = db.query(Gateway).all()
    domains = db.query(Domain).all()
    
    # 첫 번째 도메인 정보 사용 (호환성 유지)
    domain = domains[0] if domains else None
    
    summary = {
        "domain_id": domain.domain_id if domain else "",
        "domain_name": domain.name if domain else "N/A",
        "domain_shmkey": domain.shmkey if domain else None,
        "domain_tportno": domain.tportno if domain else None,
        "domain_racport": domain.racport if domain else None,
        "domain_maxuser": domain.maxuser if domain else None,
        "domain_maxnode": domain.maxnode if domain else None,
        "domain_maxsvg": domain.maxsvg if domain else None,
        "domain_maxsvr": domain.maxsvr if domain else None,
        "domain_maxsvc": domain.maxsvc if domain else None,
        "domain_maxgw": domain.maxgw if domain else None,
        "domain_maxsession": domain.maxsession if domain else None,
        "domain_security": domain.security if domain else None,
        "domain_loglvl": domain.loglvl if domain else None,
        "total_domains": len(domains),
        "total_nodes": len(nodes),
        "total_server_groups": len(svrgroups),
        "total_servers": len(servers),
        "total_services": len(services),
        "total_gateways": len(gateways),
        "nodes": [node.name for node in nodes],
        "server_groups": [svg.name for svg in svrgroups[:20]]
    }
    
    return {
        "success": True,
        "summary": summary,
        "last_update": system.get_last_update().isoformat()
    }


@router.get("/config/full")
async def get_full_config(db: Session = Depends(get_db)):
    """전체 설정 데이터 반환"""
    nodes = db.query(Node).all()
    svrgroups = db.query(SvrGroup).all()
    servers = db.query(Server).all()
    services = db.query(Service).all()
    gateways = db.query(Gateway).all()
    domain = db.query(Domain).first()
    
    return {
        "success": True,
        "data": {
            "domain": {
                "domain_id": domain.domain_id if domain else "",
                "name": domain.name if domain else ""
            },
            "nodes": [{
                "name": n.name,
                "hostname": n.hostname,
                "port": n.tmax_port
            } for n in nodes],
            "svrgroups": [{
                "name": s.name,
                "node": s.node_name
            } for s in svrgroups],
            "servers": [{
                "name": s.name,
                "svg": s.svg_name
            } for s in servers],
            "services": [{
                "name": s.name,
                "server": s.server_name
            } for s in services],
            "gateways": [{
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
        },
        "last_update": system.get_last_update().isoformat()
    }


@router.get("/node/{name}")
async def get_node(name: str, db: Session = Depends(get_db)):
    """특정 노드 정보 반환"""
    node = db.query(Node).filter(Node.name == name).first()
    
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # 이 노드의 서버 그룹 찾기
    server_groups = db.query(SvrGroup).filter(SvrGroup.node_name == name).all()
    
    return {
        "success": True,
        "node_name": node.name,
        "hostname": node.hostname,
        "port": node.tmax_port,
        "server_groups": [svg.name for svg in server_groups],
        "max_servers": node.max_svr,
        "max_users": node.max_user,
        "tmax_home": node.tmax_home
    }


@router.get("/svrgroup/{name}")
async def get_svrgroup(name: str, db: Session = Depends(get_db)):
    """특정 서버 그룹 정보 반환"""
    svrgroup = db.query(SvrGroup).filter(SvrGroup.name == name).first()
    
    if not svrgroup:
        raise HTTPException(status_code=404, detail="Server group not found")
    
    # 이 서버 그룹의 서버들 찾기
    servers = db.query(Server).filter(Server.svg_name == name).all()
    
    return {
        "success": True,
        "svg_name": svrgroup.name,
        "node": svrgroup.node_name,
        "backup": svrgroup.backup,
        "cousin": svrgroup.cousin,
        "restart": svrgroup.restart,
        "autobackup": svrgroup.autobackup,
        "servers": [{
            "name": s.name,
            "min": s.min_proc,
            "max": s.max_proc,
            "restart": s.restart
        } for s in servers]
    }


@router.get("/nodes")
async def get_all_nodes(db: Session = Depends(get_db)):
    """모든 노드 정보 반환"""
    nodes = db.query(Node).all()
    
    node_list = []
    for node in nodes:
        server_groups = db.query(SvrGroup).filter(SvrGroup.node_name == node.name).all()
        node_list.append({
            "node_name": node.name,
            "hostname": node.hostname,
            "port": node.tmax_port,
            "server_groups": [svg.name for svg in server_groups],
            "max_servers": node.max_svr,
            "max_users": node.max_user,
            "tmax_home": node.tmax_home
        })
    
    return {
        "success": True,
        "nodes": node_list,
        "total": len(node_list)
    }


@router.get("/svrgroups")
async def get_all_svrgroups(db: Session = Depends(get_db)):
    """모든 서버 그룹 정보 반환"""
    svrgroups = db.query(SvrGroup).all()
    
    svg_list = []
    for svg in svrgroups:
        servers = db.query(Server).filter(Server.svg_name == svg.name).all()
        svg_list.append({
            "svg_name": svg.name,
            "node": svg.node_name,
            "backup": svg.backup,
            "cousin": svg.cousin,
            "restart": svg.restart,
            "autobackup": svg.autobackup,
            "servers": [{
                "name": s.name,
                "min": s.min_proc,
                "max": s.max_proc,
                "restart": s.restart
            } for s in servers]
        })
    
    return {
        "success": True,
        "server_groups": svg_list,
        "total": len(svg_list)
    }
