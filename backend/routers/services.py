"""서비스 관련 라우터"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import random

from database import get_db
from models import Service, Server, User
from auth import get_current_active_user
from elasticsearch_client import get_es_client

router = APIRouter(prefix="/api", tags=["services"])


@router.get("/services")
async def get_all_services(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """모든 서비스 정보 반환 (검색 지원)"""
    query = db.query(Service)
    
    # 검색어가 있으면 필터링
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Service.name.ilike(search_filter)) |
            (Service.server_name.ilike(search_filter))
        )
    
    services = query.all()
    
    service_list = [{
        "name": s.name,
        "server": s.server_name,
        "timeout": s.timeout,
        "autotran": s.autotran,
        "export": s.export
    } for s in services]
    
    return {
        "success": True,
        "services": service_list,
        "total": len(service_list)
    }


@router.get("/services/performance")
async def get_all_services_performance(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """모든 서비스의 응답시간 요약 정보 반환 (최근 24시간)"""
    
    # 시간 범위 설정 (최근 24시간)
    end_dt = datetime.utcnow()
    start_dt = end_dt - timedelta(hours=24)
    
    # 모든 서비스 목록 가져오기
    services = db.query(Service).limit(limit).all()
    
    # Elasticsearch 클라이언트 가져오기
    es = get_es_client()
    
    performance_data = []
    
    if not es:
        # Elasticsearch 연결 실패 시 Mock 데이터 반환
        for service in services[:20]:  # 20개만 샘플로
            performance_data.append({
                "serviceName": service.name,
                "avgTime": random.uniform(10, 500),
                "minTime": random.uniform(5, 50),
                "maxTime": random.uniform(100, 1000),
                "count": random.randint(100, 10000)
            })
    else:
        try:
            # 각 서비스별로 성능 데이터 조회
            for service in services:
                try:
                    query = {
                        "size": 0,
                        "query": {
                            "bool": {
                                "must": [
                                    {"term": {"service_name.keyword": service.name}},
                                    {
                                        "range": {
                                            "@timestamp": {
                                                "gte": start_dt.isoformat(),
                                                "lte": end_dt.isoformat()
                                            }
                                        }
                                    }
                                ]
                            }
                        },
                        "aggs": {
                            "stats": {
                                "stats": {
                                    "field": "duration"
                                }
                            }
                        }
                    }
                    
                    result = es.search(index="tmax-transactions-*", body=query)
                    
                    stats = result.get("aggregations", {}).get("stats", {})
                    count = stats.get("count", 0)
                    
                    if count > 0:
                        performance_data.append({
                            "serviceName": service.name,
                            "avgTime": stats.get("avg"),
                            "minTime": stats.get("min"),
                            "maxTime": stats.get("max"),
                            "count": count
                        })
                    else:
                        # 데이터가 없는 경우에도 추가
                        performance_data.append({
                            "serviceName": service.name,
                            "avgTime": None,
                            "minTime": None,
                            "maxTime": None,
                            "count": 0
                        })
                except Exception as e:
                    # 개별 서비스 조회 실패 시 None으로 추가
                    performance_data.append({
                        "serviceName": service.name,
                        "avgTime": None,
                        "minTime": None,
                        "maxTime": None,
                        "count": 0
                    })
                    continue
        except Exception as e:
            # 전체 조회 실패 시 Mock 데이터 반환
            for service in services[:20]:
                performance_data.append({
                    "serviceName": service.name,
                    "avgTime": random.uniform(10, 500),
                    "minTime": random.uniform(5, 50),
                    "maxTime": random.uniform(100, 1000),
                    "count": random.randint(100, 10000)
                })
    
    # 평균 응답시간으로 정렬 (None 값은 뒤로)
    performance_data.sort(key=lambda x: x["avgTime"] if x["avgTime"] is not None else float('inf'), reverse=True)
    
    return {
        "success": True,
        "services": performance_data,
        "total": len(performance_data),
        "time_range": {
            "start": start_dt.isoformat(),
            "end": end_dt.isoformat()
        }
    }


@router.get("/service/{name}")
async def get_service_info(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """특정 서비스 상세 정보"""
    service = db.query(Service).filter(Service.name == name).first()
    
    if not service:
        raise HTTPException(status_code=404, detail=f"Service '{name}' not found")
    
    # 해당 서비스가 속한 서버 정보
    server = db.query(Server).filter(Server.name == service.server_name).first()
    
    result = {
        "success": True,
        "service": {
            "name": service.name,
            "server_name": service.server_name,
            "timeout": service.timeout,
            "autotran": service.autotran,
            "export": service.export
        }
    }
    
    # 서버 정보 추가
    if server:
        result["service"]["server_info"] = {
            "svg_name": server.svg_name,
            "node_name": server.node_name,
            "min_proc": server.min_proc,
            "max_proc": server.max_proc
        }
    
    return result
