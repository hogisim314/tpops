# K8s 배포 가이드

## 사전 요구사항

- Docker Desktop with Kubernetes enabled
- kubectl CLI tool
- Skaffold CLI tool
- **로컬 PostgreSQL** (K8s 외부에서 실행)
- **회사 Elasticsearch** (K8s 외부에서 접근)

## 환경 설정

### 1. 로컬 PostgreSQL 설정

로컬에 PostgreSQL을 실행해야 합니다:

```bash
# Docker로 PostgreSQL 실행 (예시)
docker run -d \
  --name tpops-postgres \
  -e POSTGRES_USER=tpops \
  -e POSTGRES_PASSWORD=tpops123 \
  -e POSTGRES_DB=tpops \
  -p 5432:5432 \
  postgres:15-alpine

# 또는 로컬에 설치된 PostgreSQL 사용
# DB와 사용자를 미리 생성해주세요
```

### 2. ConfigMap 업데이트

`k8s/configmap.yaml` 파일에서 실제 주소로 변경:

```yaml
data:
  # Mac Docker Desktop의 경우
  DATABASE_URL: "postgresql://tpops:tpops123@host.docker.internal:5432/tpops"

  # Minikube 사용시
  # DATABASE_URL: "postgresql://tpops:tpops123@host.minikube.internal:5432/tpops"

  # 회사 Elasticsearch 실제 주소로 변경
  ELASTICSEARCH_HOST: "http://your-company-elasticsearch:9200"
```

## 빠른 시작

### 1. Skaffold로 개발 환경 실행

```bash
# 모든 서비스 빌드 및 배포
skaffold dev

# 또는 백그라운드 실행
skaffold run
```

### 2. 수동 배포

```bash
# 네임스페이스 생성
kubectl apply -f k8s/namespace.yaml

# Secret과 ConfigMap 적용
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml

# 이미지 빌드
docker build -f Dockerfile.backend -t tpops-backend .
docker build -f Dockerfile.frontend -t tpops-frontend .

# 애플리케이션 배포
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# (선택) Ingress 배포
kubectl apply -f k8s/ingress.yaml
```

## 서비스 접근

### Frontend

```bash
# LoadBalancer 타입 서비스의 IP 확인
kubectl get svc frontend -n tpops

# 포트 포워딩으로 로컬 접근
kubectl port-forward svc/frontend 8080:80 -n tpops
# 브라우저에서 http://localhost:8080 접속
```

### Backend

```bash
# 포트 포워딩으로 로컬 접근
kubectl port-forward svc/backend 8000:8000 -n tpops
# 브라우저에서 http://localhost:8000/docs 접속 (Swagger UI)
```

## 리소스 확인

```bash
# 전체 리소스 확인
kubectl get all -n tpops

# Pod 상태 확인
kubectl get pods -n tpops

# Pod 로그 확인
kubectl logs -f <pod-name> -n tpops

# 서비스 확인
kubectl get svc -n tpops
```

## 디버깅

```bash
# Pod 내부 접속
kubectl exec -it <pod-name> -n tpops -- /bin/sh

# 이벤트 확인
kubectl get events -n tpops --sort-by='.lastTimestamp'

# describe로 상세 정보 확인
kubectl describe pod <pod-name> -n tpops
kubectl describe svc <service-name> -n tpops
```

## 정리

```bash
# Skaffold로 배포한 경우
skaffold delete

# 수동으로 배포한 경우
kubectl delete namespace tpops
```

## 환경 변수 설정

ConfigMap에서 데이터베이스와 Elasticsearch 주소를 설정합니다:

```bash
# ConfigMap 직접 편집
kubectl edit configmap tpops-config -n tpops

# 또는 파일 수정 후 재적용
# k8s/configmap.yaml 파일을 수정한 후:
kubectl apply -f k8s/configmap.yaml

# Secret 수정 (JWT 키, DB 비밀번호 등)
kubectl edit secret tpops-secret -n tpops

# 변경 후 Pod 재시작
kubectl rollout restart deployment/backend -n tpops
kubectl rollout restart deployment/frontend -n tpops
```

### 네트워크 설정 참고

- **Docker Desktop for Mac**: `host.docker.internal` 사용
- **Minikube**: `host.minikube.internal` 또는 Minikube VM의 호스트 IP 사용
- **Linux**: 호스트의 실제 IP 주소 사용 (예: `192.168.1.100`)
- **회사 Elasticsearch**: 실제 서버 주소와 포트 사용

## 스케일링

```bash
# Backend 복제본 수 조정
kubectl scale deployment backend --replicas=3 -n tpops

# Frontend 복제본 수 조정
kubectl scale deployment frontend --replicas=2 -n tpops
```

## Ingress 사용 (Traefik)

Traefik Ingress Controller를 사용합니다:

```bash
# Traefik이 이미 설치되어 있는지 확인
kubectl get ingressclass

# /etc/hosts에 추가 (로컬 테스트용)
echo "127.0.0.1 tpops.local" | sudo tee -a /etc/hosts

# Ingress 배포
kubectl apply -f k8s/ingress.yaml

# Traefik을 통해 접속
# 브라우저에서 http://tpops.local 접속
```

### Traefik Dashboard (선택사항)

Traefik Dashboard에서 라우팅 확인:

```bash
# Traefik 대시보드 포트 포워딩
kubectl port-forward -n kube-system $(kubectl get pods -n kube-system -l app.kubernetes.io/name=traefik -o name) 9000:9000

# 브라우저에서 http://localhost:9000/dashboard/ 접속
```
