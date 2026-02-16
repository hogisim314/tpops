"""
데이터베이스 모델 정의
"""

from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


class UserRole(str, enum.Enum):
    """사용자 역할"""
    DEVELOPER = "developer"      # 개발자
    INFRASTRUCTURE = "infrastructure"  # 인프라팀
    ADMIN = "admin"              # Tmax 관리자


class User(Base):
    """사용자 정보"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.DEVELOPER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)


class Domain(Base):
    """도메인 정보"""
    __tablename__ = "domains"
    
    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(String, unique=True, index=True)
    name = Column(String)
    shmkey = Column(String, nullable=True)
    tportno = Column(String, nullable=True)
    racport = Column(String, nullable=True)
    maxuser = Column(String, nullable=True)
    maxnode = Column(String, nullable=True)
    maxsvg = Column(String, nullable=True)
    maxsvr = Column(String, nullable=True)
    maxsvc = Column(String, nullable=True)
    maxgw = Column(String, nullable=True)
    maxsession = Column(String, nullable=True)
    security = Column(String, nullable=True)
    loglvl = Column(String, nullable=True)
    # 추가 속성들을 JSON으로 저장할 수도 있지만, 명확하게 컬럼으로 정의
    attributes = Column(Text)  # JSON 문자열로 저장


class Node(Base):
    """노드 정보"""
    __tablename__ = "nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    hostname = Column(String)
    tmax_port = Column(String)
    max_svr = Column(String)
    max_user = Column(String)
    tmax_home = Column(String)
    
    # 관계
    server_groups = relationship("SvrGroup", back_populates="node")


class SvrGroup(Base):
    """서버 그룹 정보"""
    __tablename__ = "svrgroups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    node_name = Column(String, ForeignKey("nodes.name"))
    backup = Column(String)
    cousin = Column(String)
    restart = Column(String)
    autobackup = Column(String)
    
    # 관계
    node = relationship("Node", back_populates="server_groups")
    servers = relationship("Server", back_populates="svrgroup")


class Server(Base):
    """서버 정보"""
    __tablename__ = "servers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    svg_name = Column(String, ForeignKey("svrgroups.name"))
    node_name = Column(String)
    min_proc = Column(String)
    max_proc = Column(String)
    restart = Column(String)
    maxqcount = Column(String)  # INFRASTRUCTURE 이상만 볼 수 있음
    asqcount = Column(String)   # INFRASTRUCTURE 이상만 볼 수 있음
    clopt = Column(Text)  # CLOPT 전체 값
    db_info = Column(String)  # DB 연결 정보 (예: DBU01:CORCON1), INFRASTRUCTURE 이상만 볼 수 있음
    
    # 관계
    svrgroup = relationship("SvrGroup", back_populates="servers")


class Service(Base):
    """서비스 정보"""
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    server_name = Column(String)  # ForeignKey 제거
    timeout = Column(String)
    autotran = Column(String)
    export = Column(String)


class Gateway(Base):
    """게이트웨이 정보"""
    __tablename__ = "gateways"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    node_name = Column(String)
    port = Column(String)
    remote_addr = Column(String)
    remote_port = Column(String)
    direction = Column(String)
    gw_type = Column(String)
    backup_addr = Column(String, nullable=True)
    backup_port = Column(String, nullable=True)
    backup_rgwaddr = Column(String, nullable=True)
    backup_rgwportno = Column(String, nullable=True)
    cpc = Column(String, nullable=True)
    restart = Column(String, nullable=True)
    clopt = Column(String, nullable=True)
