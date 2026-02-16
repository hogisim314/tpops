"""성능 데이터 관련 라우터"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import Service, User
from auth import get_current_active_user
from elasticsearch_client import get_es_client, ES_INDEX_PREFIX
from utils.mock_data import generate_mock_performance_data

router = APIRouter(prefix="/api", tags=["performance"])


def calculate_interval(start_dt: datetime, end_dt: datetime) -> str:
    """시간 범위에 따라 적절한 interval 계산"""
    duration = end_dt - start_dt
    
    if duration.days >= 7:
        return "1h"
    elif duration.days >= 1:
        return "30m"
    elif duration.total_seconds() >= 3600:
        return "5m"
    else:
        return "1m"


@router.get("/performance/{service_name}")
async def get_service_performance(
    service_name: str,
    start: str,
    end: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    서비스(TR) 성능 데이터 조회 (Elasticsearch)
    
    Parameters:
    - service_name: 서비스 이름
    - start: 시작 시간 (ISO format: 2024-01-01T00:00)
    - end: 종료 시간 (ISO format: 2024-01-01T23:59)
    """
    # 서비스 존재 확인
    service = db.query(Service).filter(Service.name == service_name).first()
    if not service:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
    
    # Elasticsearch 클라이언트 가져오기
    es = get_es_client()
    if not es:
        # Elasticsearch 연결 실패 시 Mock 데이터 반환
        return generate_mock_performance_data(service_name, start, end)
    
    try:
        # 시간 범위 변환
        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
        
        # Elasticsearch 쿼리
        query = {
            "size": 0,
            "query": {
                "bool": {
                    "must": [
                        {"term": {"service_name.keyword": service_name}},
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
                },
                "percentiles": {
                    "percentiles": {
                        "field": "duration",
                        "percents": [50, 95, 99]
                    }
                },
                "time_series": {
                    "date_histogram": {
                        "field": "@timestamp",
                        "fixed_interval": calculate_interval(start_dt, end_dt),
                        "time_zone": "Asia/Seoul"
                    },
                    "aggs": {
                        "avg_duration": {
                            "avg": {
                                "field": "duration"
                            }
                        }
                    }
                },
                "slow_transactions": {
                    "top_hits": {
                        "size": 10,
                        "sort": [
                            {"duration": {"order": "desc"}}
                        ],
                        "_source": ["@timestamp", "duration", "status"]
                    }
                }
            }
        }
        
        # 쿼리 실행
        result = es.search(index=f"{ES_INDEX_PREFIX}-*", body=query)
        
        # 결과 파싱
        stats_agg = result["aggregations"]["stats"]
        percentiles_agg = result["aggregations"]["percentiles"]["values"]
        time_series_buckets = result["aggregations"]["time_series"]["buckets"]
        slow_txs = result["aggregations"]["slow_transactions"]["hits"]["hits"]
        
        return {
            "avgTime": stats_agg["avg"] or 0,
            "minTime": stats_agg["min"] or 0,
            "maxTime": stats_agg["max"] or 0,
            "medianTime": percentiles_agg.get("50.0", 0),
            "count": int(stats_agg["count"]),
            "slowTransactions": [
                {
                    "timestamp": tx["_source"]["@timestamp"],
                    "duration": tx["_source"]["duration"],
                    "status": tx["_source"].get("status", "unknown")
                }
                for tx in slow_txs
            ],
            "timeSeriesData": [
                {
                    "timestamp": bucket["key_as_string"],
                    "avgDuration": bucket["avg_duration"]["value"] or 0,
                    "count": bucket["doc_count"]
                }
                for bucket in time_series_buckets
            ]
        }
        
    except Exception as e:
        print(f"Elasticsearch 쿼리 오류: {e}")
        # 오류 시 Mock 데이터 반환
        return generate_mock_performance_data(service_name, start, end)
