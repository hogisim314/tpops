#!/bin/bash

# 프론트엔드 실행 스크립트

echo "========================================"
echo "프론트엔드 개발 서버 시작"
echo "React TypeScript + Vite"
echo "========================================"

cd frontend

# 의존성이 설치되지 않은 경우
if [ ! -d "node_modules" ]; then
    echo "📦 npm 의존성 설치 중..."
    npm install
fi

echo ""
echo "🚀 프론트엔드 서버 시작 중..."
echo "   Frontend: http://localhost:3000"
echo ""
echo "백엔드가 실행 중인지 확인하세요:"
echo "   Backend: http://localhost:8080"
echo ""
echo "========================================"

# Vite 개발 서버 실행
npm run dev
