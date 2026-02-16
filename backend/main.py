from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from pathlib import Path
import os
import re
import io
import random
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

from parser import TpConfigParser
from database import get_db, init_db, engine
from models import Domain, Node, SvrGroup, Server, Service, Gateway, User, UserRole
from auth import get_password_hash

# 라우터 import
from routers import auth, config, servers, services, performance, export, gateways, users, system

app = FastAPI(
    title="Tmax Monitoring Dashboard API",
    version="2.0.0",
    description="FastAPI + React TypeScript"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수
last_update: datetime


def extract_db_info(clopt: str) -> str:
    """
    CLOPT 필드에서 DB 연결 정보 추출
    예: "... -- -k DBU01:CORCON1" -> "DBU01:CORCON1"
    """
    if not clopt:
        return ""
    
    # -- -k 다음의 값 추출
    match = re.search(r'--\s+-k\s+(\S+)', clopt)
    if match:
        return match.group(1)
    
    return ""


def map_db_to_display(db_info: str) -> str:
    """
    DB 정보를 화면 표시용으로 매핑
    예: "DBU01:CORCON1" -> "DB1호기", "DBU02:CORCON1" -> "DB2호기"
    """
    if not db_info:
        return ""
    
    # DBU01, DBU02, DBU03, DBU04 등을 추출
    match = re.search(r'DBU0?(\d+)', db_info)
    if match:
        db_num = match.group(1)
        return f"DB{db_num}호기"
    
    return db_info

# 프로젝트 루트 디렉토리 (backend의 상위 디렉토리)
CONFIG_DIR = os.path.dirname(os.path.dirname(__file__)) or "."


def get_config_files():
    """프로젝트 루트의 scorap*.m 파일 목록 반환"""
    config_files = []
    root_dir = Path(CONFIG_DIR)
    
    # scorap로 시작하고 .m으로 끝나는 모든 파일 찾기
    for file in root_dir.glob("scorap*.m"):
        if file.is_file():
            config_files.append(file.name)
    
    return sorted(config_files)


def load_all_configs_to_db(db: Session):
    """모든 config 파일을 통합하여 DB에 저장"""
    global last_update
    
    # 기존 데이터 삭제
    db.query(Gateway).delete()
    db.query(Service).delete()
    db.query(Server).delete()
    db.query(SvrGroup).delete()
    db.query(Node).delete()
    db.query(Domain).delete()
    db.commit()  # 삭제를 즉시 반영
    
    # 중복 추적용 set
    added_domains = set()
    added_nodes = set()
    added_svrgroups = set()
    added_services = set()
    added_gateways = set()
    
    config_files = get_config_files()
    
    for config_file in config_files:
        config_path = os.path.join(CONFIG_DIR, config_file)
        if not os.path.exists(config_path):
            continue
        
        # config 파일 파싱
        parser = TpConfigParser(config_path)
        config_data = parser.parse()
        
        # Domain 저장
        if config_data["domain"]:
            domain_data = config_data["domain"]
            domain_id = domain_data.get("DOMAINID", "")
            
            # 메모리에서 중복 체크 (여러 config 파일 간 중복 방지)
            if domain_id not in added_domains:
                added_domains.add(domain_id)
                domain = Domain(
                    domain_id=domain_id,
                    name=domain_data.get("name", "N/A"),
                    shmkey=domain_data.get("SHMKEY", ""),
                    tportno=domain_data.get("TPORTNO", ""),
                    racport=domain_data.get("RACPORT", ""),
                    maxuser=domain_data.get("MAXUSER", ""),
                    maxnode=domain_data.get("MAXNODE", ""),
                    maxsvg=domain_data.get("MAXSVG", ""),
                    maxsvr=domain_data.get("MAXSVR", ""),
                    maxsvc=domain_data.get("MAXSVC", ""),
                    maxgw=domain_data.get("MAXGW", ""),
                    maxsession=domain_data.get("MAXSESSION", ""),
                    security=domain_data.get("SECURITY", ""),
                    loglvl=domain_data.get("LOGLVL", ""),
                    attributes=str(domain_data)
                )
                db.add(domain)
        
        # Node 저장
        for node_name, node_data in config_data["node"].items():
            # 메모리에서 중복 체크
            if node_name in added_nodes:
                continue
            added_nodes.add(node_name)
            
            node = Node(
                name=node_name,
                hostname=node_data.get("HOSTNAME", ""),
                tmax_port=node_data.get("TmaxPort", ""),
                max_svr=node_data.get("MAXSVR", ""),
                max_user=node_data.get("MAXUSER", ""),
                tmax_home=node_data.get("TMAXHOME", "")
            )
            db.add(node)
        
        # SvrGroup 저장
        for svg_name, svg_data in config_data["svrgroup"].items():
            # 메모리에서 중복 체크
            if svg_name in added_svrgroups:
                continue
            added_svrgroups.add(svg_name)
            
            svrgroup = SvrGroup(
                name=svg_name,
                node_name=svg_data.get("NODENAME", "").strip('"'),
                backup=svg_data.get("BACKUP", "N/A").strip('"'),
                cousin=svg_data.get("COUSIN", "N/A").strip('"'),
                restart=svg_data.get("RESTART", ""),
                autobackup=svg_data.get("AUTOBACKUP", "")
            )
            db.add(svrgroup)
        
        # 첫 번째 노드 이름 가져오기 (기본값으로 사용)
        first_node_name = list(config_data["node"].keys())[0] if config_data["node"] else ""
        
        # Server 저장
        for srv_name, srv_list in config_data["server"].items():
            for srv_data in srv_list:
                # CLOPT에서 DB 정보 추출
                clopt = srv_data.get("CLOPT", "")
                db_info = extract_db_info(clopt)
                
                # NODENAME이 없거나 비어있으면 첫 번째 노드 사용
                node_name = srv_data.get("NODENAME", "").strip('"')
                if not node_name:
                    node_name = first_node_name
                
                server = Server(
                    name=srv_name,
                    svg_name=srv_data.get("SVGNAME", "").strip('"'),
                    node_name=node_name,
                    min_proc=srv_data.get("MIN", ""),
                    max_proc=srv_data.get("MAX", ""),
                    restart=srv_data.get("RESTART", ""),
                    maxqcount=srv_data.get("MAXQCOUNT", ""),
                    asqcount=srv_data.get("ASQCOUNT", ""),
                    clopt=clopt,
                    db_info=db_info
                )
                db.add(server)
        
        # Service 저장
        for svc_name, svc_data in config_data["service"].items():
            # 메모리에서 중복 체크 (여러 config 파일 간 중복 방지)
            if svc_name in added_services:
                continue
            added_services.add(svc_name)
            
            service = Service(
                name=svc_name,
                server_name=svc_data.get("SVRNAME", "").strip('"'),
                timeout=svc_data.get("SVCTIME", ""),
                autotran=svc_data.get("AUTOTRAN", ""),
                export=svc_data.get("EXPORT", "")
            )
            db.add(service)
        
        # Gateway 저장
        for gw_name, gw_data in config_data["gateway"].items():
            # 메모리에서 중복 체크
            if gw_name in added_gateways:
                continue
            added_gateways.add(gw_name)
            
            gateway = Gateway(
                name=gw_name,
                node_name=gw_data.get("NODENAME", "").strip('"'),
                port=gw_data.get("PORTNO", ""),
                remote_addr=gw_data.get("RGWADDR", "").strip('"'),
                remote_port=gw_data.get("RGWPORTNO", ""),
                direction=gw_data.get("DIRECTION", ""),
                gw_type=gw_data.get("GWTYPE", ""),
                backup_addr=gw_data.get("BACKUPIP", "").strip('"') if gw_data.get("BACKUPIP") else None,
                backup_port=gw_data.get("BACKUPPORT", "") if gw_data.get("BACKUPPORT") else None,
                backup_rgwaddr=gw_data.get("BACKUP_RGWADDR", "").strip('"') if gw_data.get("BACKUP_RGWADDR") else None,
                backup_rgwportno=gw_data.get("BACKUP_RGWPORTNO", "") if gw_data.get("BACKUP_RGWPORTNO") else None,
                cpc=gw_data.get("CPC", ""),
                restart=gw_data.get("RESTART", ""),
                clopt=gw_data.get("CLOPT", "").strip('"') if gw_data.get("CLOPT") else None
            )
            db.add(gateway)
    
    db.commit()
    last_update = datetime.now()
    
    
@app.on_event("startup")
async def startup_event():
    """서버 시작 시 DB 초기화 및 설정 로드"""
    config_files = get_config_files()
    if not config_files:
        raise RuntimeError(f"Error: No config files found in '{CONFIG_DIR}' directory!")
    
    # DB 테이블 생성
    init_db()
    
    # 모든 설정 파일을 통합하여 DB에 로드
    db = next(get_db())
    try:
        load_all_configs_to_db(db)
        
        # 기본 사용자 생성 (없으면)
        if db.query(User).count() == 0:
            default_users = [
                User(
                    username="admin",
                    email="admin@tmax.com",
                    hashed_password=get_password_hash("admin"),
                    full_name="System Administrator",
                    role=UserRole.ADMIN
                ),
                User(
                    username="service",
                    email="service@tmax.com",
                    hashed_password=get_password_hash("service"),
                    full_name="Service Team",
                    role=UserRole.INFRASTRUCTURE
                ),
                User(
                    username="monitoring",
                    email="monitoring@tmax.com",
                    hashed_password=get_password_hash("monitoring"),
                    full_name="Monitoring User",
                    role=UserRole.DEVELOPER
                )
            ]
            for user in default_users:
                db.add(user)
            db.commit()
            print("✅ Default users created")
    finally:
        db.close()
    
    print("==================================================")
    print("🚀 Tmax Monitoring Dashboard Starting...")
    print("==================================================")
    print(f"📁 Config files: {', '.join(get_config_files())}")
    print(f"💾 Database: PostgreSQL")
    print(f"🌐 Backend URL: http://localhost:8080")
    print(f"🔧 API URL: http://localhost:8080/api/config")
    print("==================================================")


# 라우터 등록
app.include_router(auth.router)
app.include_router(config.router)
app.include_router(servers.router)
app.include_router(services.router)
app.include_router(performance.router)
app.include_router(export.router)
app.include_router(gateways.router)
app.include_router(users.router)
app.include_router(system.router)


@app.get("/")
async def home():
    """홈 엔드포인트"""
    return {
        "message": "Tmax Monitoring Dashboard API",
        "version": "2.0.0",
        "tech": "FastAPI + React TypeScript + PostgreSQL",
        "features": ["Multi-tenant", "RBAC", "JWT Auth", "Modular Architecture"]
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트 (Kubernetes 프로브용)"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
