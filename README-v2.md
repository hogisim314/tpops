# Tmax 모니터링 대시보드 v2.0

React TypeScript + Golang으로 구현된 Tmax 시스템 모니터링 대시보드입니다.

## 🛠️ 기술 스택

### 프론트엔드

- **React 18** - UI 라이브러리
- **TypeScript** - 타입 안정성
- **Vite** - 빠른 빌드 도구
- **Axios** - HTTP 클라이언트

### 백엔드

- **Go 1.21+** - 고성능 백엔드
- **Gorilla Mux** - HTTP 라우터
- **CORS** - Cross-Origin 지원

## 📁 프로젝트 구조

```
tpops/
├── backend/                 # Go 백엔드
│   ├── main.go             # 메인 서버
│   ├── parser.go           # tp_config 파서
│   └── go.mod              # Go 의존성
├── frontend/               # React 프론트엔드
│   ├── src/
│   │   ├── components/     # React 컴포넌트
│   │   ├── App.tsx         # 메인 앱
│   │   ├── api.ts          # API 클라이언트
│   │   ├── types.ts        # TypeScript 타입
│   │   └── main.tsx        # 엔트리 포인트
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
└── tp_config_20260126      # Tmax 설정 파일
```

## 🚀 시작하기

### 필수 요구사항

- **Go 1.21 이상**
- **Node.js 18 이상**
- **npm 또는 yarn**

### 1. 백엔드 설정

```bash
cd backend

# Go 의존성 설치
go mod download

# tp_config 파일을 backend 디렉토리로 복사 (또는 심볼릭 링크)
ln -s ../tp_config_20260126 ./tp_config_20260126

# 백엔드 서버 실행
go run .
```

백엔드 서버가 http://localhost:8080 에서 실행됩니다.

### 2. 프론트엔드 설정

```bash
cd frontend

# npm 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

프론트엔드가 http://localhost:3000 에서 실행됩니다.

## 🔧 API 엔드포인트

### 기본

- `GET /api/health` - 헬스 체크
- `GET /api/config` - 전체 설정 요약
- `GET /api/config/full` - 전체 설정 데이터
- `GET /api/reload` - 설정 재로드

### 노드

- `GET /api/nodes` - 모든 노드 목록
- `GET /api/node/{name}` - 특정 노드 상세

### 서버 그룹

- `GET /api/svrgroups` - 모든 서버 그룹 목록
- `GET /api/svrgroup/{name}` - 특정 서버 그룹 상세

### 기타

- `GET /api/servers` - 모든 서버 목록
- `GET /api/services` - 모든 서비스 목록
- `GET /api/gateways` - 게이트웨이 목록

## 🏗️ 프로덕션 빌드

### 프론트엔드 빌드

```bash
cd frontend
npm run build
```

빌드된 파일은 `frontend/dist` 디렉토리에 생성됩니다.

### 백엔드 빌드

```bash
cd backend
go build -o tpops-server
```

실행 파일 `tpops-server`가 생성됩니다.

### 배포

```bash
# 백엔드 실행
cd backend
./tpops-server

# 프론트엔드는 Nginx 등의 웹 서버로 서빙
# 또는 Go 서버에서 static 파일 서빙 추가
```

## ✨ 주요 기능

- ✅ 실시간 대시보드 (30초 자동 갱신)
- ✅ 노드별 상세 정보
- ✅ 서버 그룹별 서버 목록
- ✅ TypeScript 타입 안정성
- ✅ Go의 고성능 파싱
- ✅ 반응형 UI
- ✅ 모달 기반 상세 정보 조회

## 🔄 주요 변경사항 (v1 → v2)

### 백엔드

- Python Flask → **Go (Golang)**
- 정규표현식 기반 파서 유지
- RESTful API 동일하게 유지
- 성능 향상 및 메모리 효율성 개선

### 프론트엔드

- Vanilla JavaScript → **React + TypeScript**
- jQuery → **Axios**
- 컴포넌트 기반 아키텍처
- 타입 안정성 강화
- 개발 경험 향상 (Hot Reload)

## 🎯 개발 모드

개발 중에는 두 개의 터미널을 사용합니다:

**터미널 1 (백엔드)**:

```bash
cd backend
go run .
```

**터미널 2 (프론트엔드)**:

```bash
cd frontend
npm run dev
```

Vite의 프록시 설정으로 프론트엔드에서 백엔드 API를 자동으로 프록시합니다.

## 📊 성능

- **Go 백엔드**: 빠른 파싱 및 API 응답 (<10ms)
- **React**: Virtual DOM으로 효율적인 렌더링
- **Vite**: 빠른 Hot Module Replacement
- **TypeScript**: 컴파일 타임 에러 감지

## 🐛 문제 해결

### 백엔드 포트 충돌

```bash
# 포트 8080이 사용 중인 경우
lsof -ti:8080 | xargs kill -9
```

### 프론트엔드 포트 충돌

`frontend/vite.config.ts`에서 포트 변경:

```typescript
server: {
  port: 3001, // 원하는 포트로 변경
}
```

### CORS 오류

백엔드의 `main.go`에서 CORS 설정 확인:

```go
AllowedOrigins: []string{"http://localhost:3000"},
```

## 📝 라이선스

MIT License

## 👨‍💻 기여

Pull Request를 환영합니다!

---

**v2.0.0** - React TypeScript + Golang 완전 재구현
