# Tmax 설정 모니터링 대시보드

Tmax 시스템의 설정 파일(tp_config)을 시각화하고 모니터링하는 웹 기반 대시보드입니다.

## 주요 기능

- **실시간 대시보드**: Tmax 시스템 전체 상태를 한눈에 확인
- **노드 관리**: 모든 노드의 상세 정보와 상태 조회
- **서버 그룹 모니터링**: 서버 그룹별 서버 및 서비스 현황
- **서버/서비스 목록**: 실행 중인 모든 서버와 서비스 정보
- **게이트웨이 관리**: 게이트웨이 연결 상태 및 설정 확인
- **자동 새로고침**: 30초마다 자동으로 데이터 업데이트
- **반응형 UI**: 모던하고 직관적인 사용자 인터페이스

## 요구사항

- Docker
- Kubernetes (k3d, minikube 등)
- Skaffold

## 프로젝트 구조

```
tpops_back/
├── backend/                  # FastAPI 백엔드
│   ├── main.py               # 메인 애플리케이션
│   ├── database.py           # 데이터베이스 설정
│   ├── models.py             # SQLAlchemy 모델
│   └── routers/              # API 라우터
├── frontend/                 # React 프론트엔드
│   ├── src/
│   │   ├── App.tsx           # 메인 컴포넌트
│   │   ├── api.ts            # API 클라이언트
│   │   └── components/       # React 컴포넌트
│   └── vite.config.ts        # Vite 설정
├── k8s/                      # Kubernetes 매니페스트
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   └── ingress.yaml
├── skaffold.yaml             # Skaffold 설정 파일
└── README.md                 # 이 파일
```

## 설치 및 실행

이 프로젝트는 `skaffold`를 사용하여 로컬 Kubernetes 클러스터에서 개발 및 배포를 자동화합니다.

1.  **로컬 Kubernetes 클러스터 시작**

    `k3d` 또는 `minikube`와 같은 도구를 사용하여 로컬 클러스터를 생성합니다.

    ```bash
    # k3d 사용 예시
    k3d cluster create my-cluster
    ```

2.  **Skaffold 개발 모드 실행**

    프로젝트 루트 디렉토리에서 다음 명령어를 실행합니다.

    ```bash
    skaffold dev
    ```

    이 명령어는 다음 작업을 자동으로 수행합니다.
    - Docker 이미지 빌드
    - Kubernetes 클러스터에 애플리케이션 배포
    - 소스 코드 변경 시 자동 재배포
    - 포트 포워딩 설정

3.  **대시보드 접속**

    Skaffold가 실행되면 `ingress` 설정을 통해 대시보드에 접속할 수 있습니다. 일반적으로 `http://tpops.local`로 접속 가능합니다.

## API 엔드포인트

API는 `/api` 경로 아래에 마운트됩니다.

### 시스템 및 설정

- `GET /api/health`: 헬스 체크
- `GET /api/config/summary`: 전체 설정 요약
- `GET /api/config/reload`: 설정 파일 다시 로드

### 조회

- `GET /api/nodes`: 모든 노드 목록
- `GET /api/nodes/{node_name}`: 특정 노드 상세 정보
- `GET /api/svrgroups`: 모든 서버 그룹 목록
- `GET /api/svrgroups/{group_name}`: 특정 서버 그룹 상세 정보
- `GET /api/servers`: 모든 서버 목록
- `GET /api/services`: 모든 서비스 목록
- `GET /api/gateways`: 모든 게이트웨이 목록

### 인증

- `POST /api/auth/token`: JWT 토큰 발급

## 향후 개발 계획

- 실시간 시스템 성능 모니터링 (메모리, CPU)
- 히스토리 데이터 분석 및 시각화
- 알림 및 경고 시스템
- 서버 시작/중지 제어 기능
- 설정 파일 편집 및 적용 기능
