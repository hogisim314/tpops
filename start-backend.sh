#!/bin/bash

# Tmax 모니터링 대시보드 v2.0 실행 스크립트
# React TypeScript + FastAPI

echo "========================================"
echo "Tmax 모니터링 대시보드 v2.0 시작"
echo "React TypeScript + FastAPI"
echo "========================================"

# 설정 파일 확인
if [ ! -f "backend/config" ]; then
    echo "❌ 오류: backend/config 파일을 찾을 수 없습니다."
    exit 1
fi

echo "✅ 설정 파일 확인 완료"
echo ""

# Python 가상환경 확인 및 활성화
if [ ! -d "venv" ]; then
    echo "📦 Python 가상환경 생성 중..."
    python3 -m venv venv
fi

echo "🔧 가상환경 활성화 중..."
source venv/bin/activate

# Python 의존성 설치
echo "📦 Python 의존성 설치 중..."
pip install -q -r requirements.txt

echo ""
echo "🚀 백엔드 서버 시작 중..."
echo "   Backend: http://localhost:8080"
echo "   API Docs: http://localhost:8080/docs"
echo ""
echo "프론트엔드를 실행하려면 다른 터미널에서:"
echo "   cd frontend && npm install && npm run dev"
echo ""
echo "========================================"

# FastAPI 서버 실행
cd backend && python main.py
