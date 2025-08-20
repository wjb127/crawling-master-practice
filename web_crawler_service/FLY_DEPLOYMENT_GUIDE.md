# 🚀 Fly.io 배포 가이드

## 📋 사전 준비사항

1. **Fly.io 계정 생성**
   - https://fly.io 에서 무료 계정 생성
   - 신용카드 등록 (무료 티어 사용 가능)

2. **Fly CLI 설치**
   ```bash
   # macOS
   brew install flyctl

   # Linux
   curl -L https://fly.io/install.sh | sh

   # Windows
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

## 🎯 빠른 배포 (원클릭)

```bash
cd web_crawler_service
chmod +x deploy.sh
./deploy.sh
```

## 📝 수동 배포 단계

### 1. Fly.io 로그인
```bash
flyctl auth login
```

### 2. 앱 생성
```bash
flyctl apps create crawling-master-kr --region nrt
```
- `nrt` = Tokyo region (한국에서 가장 가까움)

### 3. 볼륨 생성 (데이터 저장용)
```bash
flyctl volumes create crawling_data --app crawling-master-kr --region nrt --size 1
```

### 4. 환경 변수 설정
```bash
flyctl secrets set \
  ENVIRONMENT=production \
  MAX_CONCURRENT_JOBS=20 \
  MAX_PAGES_PER_JOB=50 \
  RATE_LIMIT_DELAY=0.5 \
  --app crawling-master-kr
```

### 5. 배포
```bash
# 프로덕션 파일 사용
cp simple_main_prod.py simple_main.py

# 배포 실행
flyctl deploy --app crawling-master-kr --dockerfile Dockerfile.fly
```

## 🔍 배포 후 확인

### 앱 상태 확인
```bash
flyctl status --app crawling-master-kr
```

### 로그 확인
```bash
flyctl logs --app crawling-master-kr
```

### 앱 열기
```bash
flyctl open --app crawling-master-kr
# 또는 직접 접속: https://crawling-master-kr.fly.dev
```

## 💰 비용 관리

### 무료 티어
- 3개 shared-cpu-1x VMs (256MB RAM)
- 3GB 영구 볼륨 스토리지
- 160GB 아웃바운드 데이터 전송

### 현재 설정 (fly.toml)
- CPU: shared-cpu-1x
- RAM: 512MB
- Storage: 1GB
- **예상 월 비용**: $0-5 (무료 티어 내)

### 사용량 확인
```bash
flyctl dashboard --app crawling-master-kr
```

## 🔧 유용한 명령어

### 스케일링
```bash
# 인스턴스 수 조정
flyctl scale count 2 --app crawling-master-kr

# 메모리 조정
flyctl scale memory 1024 --app crawling-master-kr
```

### SSH 접속
```bash
flyctl ssh console --app crawling-master-kr
```

### 재시작
```bash
flyctl apps restart crawling-master-kr
```

### 삭제
```bash
# 앱 삭제 (주의!)
flyctl apps destroy crawling-master-kr
```

## 🚨 트러블슈팅

### 1. 포트 문제
```toml
# fly.toml에서 확인
[env]
  PORT = "8080"  # 반드시 8080 사용

[[services]]
  internal_port = 8080  # 내부 포트도 8080
```

### 2. 헬스체크 실패
```bash
# 로그 확인
flyctl logs --app crawling-master-kr

# 헬스체크 엔드포인트 확인
curl https://crawling-master-kr.fly.dev/health
```

### 3. 메모리 부족
```bash
# 메모리 증가
flyctl scale memory 1024 --app crawling-master-kr
```

### 4. 빌드 실패
```bash
# 로컬에서 Docker 빌드 테스트
docker build -f Dockerfile.fly -t test .
docker run -p 8080:8080 test
```

## 📊 모니터링

### Grafana 대시보드
```bash
flyctl dashboard metrics --app crawling-master-kr
```

### 실시간 로그
```bash
flyctl logs --app crawling-master-kr --tail
```

## 🔄 업데이트 배포

### 코드 변경 후
```bash
# 변경사항 커밋
git add .
git commit -m "Update features"

# 재배포
flyctl deploy --app crawling-master-kr
```

### 무중단 배포
Fly.io는 기본적으로 rolling deployment를 지원합니다.

## 🌍 리전 추가

### 멀티 리전 배포
```bash
# 리전 추가
flyctl regions add sin --app crawling-master-kr  # Singapore
flyctl regions add hkg --app crawling-master-kr  # Hong Kong

# 현재 리전 확인
flyctl regions list --app crawling-master-kr
```

## 📱 커스텀 도메인

### 도메인 연결
```bash
# 도메인 추가
flyctl certs create yourdomain.com --app crawling-master-kr

# DNS 설정 확인
flyctl certs show yourdomain.com --app crawling-master-kr
```

## 🔒 보안

### IP 화이트리스트
```bash
flyctl ips list --app crawling-master-kr
```

### HTTPS 인증서
자동으로 Let's Encrypt 인증서가 적용됩니다.

---

## 💡 팁

1. **개발/스테이징 환경 분리**
   ```bash
   flyctl apps create crawling-master-dev --region nrt
   ```

2. **백업**
   ```bash
   flyctl volumes snapshots list --app crawling-master-kr
   ```

3. **비용 알림 설정**
   Fly.io 대시보드에서 billing alerts 설정

## 📞 지원

- Fly.io 문서: https://fly.io/docs
- 커뮤니티: https://community.fly.io
- 상태 페이지: https://status.flyio.net

---

**Made for 크몽 Freelancers** 🕷️