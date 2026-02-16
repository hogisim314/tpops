"""
Elasticsearch 연동 설정
"""
from elasticsearch import Elasticsearch
from typing import Optional
import os

# Elasticsearch 설정 (환경변수 또는 기본값)
ES_HOST = os.getenv("ES_HOST", "localhost")
ES_PORT = int(os.getenv("ES_PORT", "9200"))
ES_USER = os.getenv("ES_USER", "")
ES_PASSWORD = os.getenv("ES_PASSWORD", "")
ES_INDEX_PREFIX = os.getenv("ES_INDEX_PREFIX", "tmax-logs")

# Elasticsearch 클라이언트 생성
def get_es_client() -> Optional[Elasticsearch]:
    """Elasticsearch 클라이언트 반환"""
    try:
        if ES_USER and ES_PASSWORD:
            es = Elasticsearch(
                [f"http://{ES_HOST}:{ES_PORT}"],
                basic_auth=(ES_USER, ES_PASSWORD),
                verify_certs=False,
                request_timeout=30
            )
        else:
            es = Elasticsearch(
                [f"http://{ES_HOST}:{ES_PORT}"],
                verify_certs=False,
                request_timeout=30
            )
        
        # 연결 테스트
        if es.ping():
            return es
        return None
    except Exception as e:
        print(f"Elasticsearch 연결 실패: {e}")
        return None
