#!/bin/bash
# Tmax 모니터링 대시보드 실행 스크립트

echo "========================================"
echo "Tmax 모니터링 대시보드 시작"
echo "========================================"

# 의존성 확인
echo "1. 필수 패키지 확인 중..."
pip3 install -q flask flask-cors 2>/dev/null

# 설정 파일 확인
if [ ! -f "tp_config_20260126" ]; then
    echo "❌ 오류: tp_config_20260126 파일을 찾을 수 없습니다."
    exit 1
fi

echo "✅ 설정 파일 확인 완료"

# Flask 서버 시작
echo "2. 웹 서버 시작 중..."
echo ""
python3 app.py
