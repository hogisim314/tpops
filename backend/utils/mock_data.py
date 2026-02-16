"""Mock 데이터 생성 유틸리티"""
import random
from datetime import datetime, timedelta


def generate_mock_performance_data(service_name: str, start: str, end: str):
    """Mock 성능 데이터 생성 (Elasticsearch 연결 실패 시 사용)"""
    
    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
    end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
    duration = end_dt - start_dt
    
    # Mock 통계 데이터
    base_avg = random.uniform(50, 200)
    
    # 시계열 데이터 생성
    num_points = min(20, max(5, int(duration.total_seconds() / 300)))  # 최대 20 포인트
    time_series = []
    
    for i in range(num_points):
        timestamp = start_dt + timedelta(seconds=duration.total_seconds() * i / num_points)
        time_series.append({
            "timestamp": timestamp.isoformat(),
            "avgDuration": base_avg + random.uniform(-30, 50),
            "count": random.randint(50, 500)
        })
    
    # 느린 트랜잭션 생성
    slow_transactions = []
    for i in range(10):
        timestamp = start_dt + timedelta(seconds=random.uniform(0, duration.total_seconds()))
        slow_transactions.append({
            "timestamp": timestamp.isoformat(),
            "duration": base_avg * random.uniform(2, 5),
            "status": random.choice(["success", "success", "success", "error"])
        })
    
    slow_transactions.sort(key=lambda x: x["duration"], reverse=True)
    
    return {
        "avgTime": base_avg,
        "minTime": base_avg * 0.3,
        "maxTime": base_avg * 4.5,
        "medianTime": base_avg * 0.9,
        "count": random.randint(1000, 10000),
        "slowTransactions": slow_transactions,
        "timeSeriesData": time_series
    }
