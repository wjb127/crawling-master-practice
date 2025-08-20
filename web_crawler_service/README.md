# 🕷️ 크롤링 마스터 - FastAPI + HTMX + Tailwind

간단하고 강력한 웹 크롤링 서비스입니다. DB 없이 메모리에서 작동하며, 결과를 엑셀 파일로 다운로드할 수 있습니다.

## ✨ 주요 기능

- 🎯 **간단한 크롤링 설정** - URL과 CSS 선택자만으로 데이터 수집
- ⚡ **실시간 진행 상황** - HTMX로 구현된 실시간 업데이트
- 📊 **엑셀 내보내기** - 스타일이 적용된 XLSX 파일 다운로드
- 🚀 **빠른 크롤링** - URL만 입력하면 자동으로 데이터 추출
- 💾 **DB 불필요** - 모든 데이터는 메모리에 저장, 파일로 다운로드

## 🚀 빠른 시작

### 방법 1: 직접 실행 (macOS/Linux)

```bash
# 실행 권한 부여
chmod +x run.sh

# 서버 시작
./run.sh
```

### 방법 2: 직접 실행 (Windows)

```batch
# 서버 시작
run.bat
```

### 방법 3: Python으로 직접 실행

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 시작
uvicorn simple_main:app --reload --host 0.0.0.0 --port 8000
```

### 방법 4: Docker 사용

```bash
# Docker Compose로 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

## 📝 사용 방법

1. **서버 시작 후 브라우저에서 접속**
   ```
   http://localhost:8000
   ```

2. **빠른 크롤링 (자동 모드)**
   - 상단의 "빠른 크롤링" 섹션에 URL 입력
   - "자동 크롤링" 버튼 클릭
   - 자동으로 제목, 내용, 이미지 등을 감지하여 수집

3. **커스텀 크롤링**
   - "새 크롤링" 버튼 클릭
   - 작업 이름과 URL 입력
   - CSS 선택자 입력 (형식: `필드명: 선택자`)
   ```
   title: h1.article-title
   content: div.article-body
   author: span.author-name
   ```

4. **결과 다운로드**
   - 크롤링 완료 후 "엑셀 다운로드" 버튼 클릭
   - 파일은 `downloads/` 폴더에 저장됨

## 🔧 CSS 선택자 예시

```yaml
# 네이버 뉴스
title: h2.media_end_head_headline
content: article#dic_area
date: span.media_end_head_info_datestamp_time

# 일반적인 블로그
title: h1, h2.post-title
content: div.post-content, article
author: span.author, div.writer

# 쇼핑몰
product_name: h1.product-name
price: span.price, div.cost
description: div.product-description
```

## 📁 프로젝트 구조

```
web_crawler_service/
├── simple_main.py          # FastAPI 메인 서버
├── templates/
│   └── index.html         # HTMX + Tailwind UI
├── downloads/             # 크롤링 결과 저장
├── requirements.txt       # Python 의존성
├── run.sh                # macOS/Linux 실행 스크립트
├── run.bat              # Windows 실행 스크립트
├── Dockerfile           # Docker 이미지
└── docker-compose.yml   # Docker Compose 설정
```

## 🛠️ 기술 스택

- **Backend**: FastAPI, aiohttp, BeautifulSoup4
- **Frontend**: HTMX, Tailwind CSS, Alpine.js
- **Data**: Pandas, OpenPyXL
- **Deployment**: Docker, Uvicorn

## ⚙️ 환경 변수 (선택사항)

`.env` 파일을 생성하여 설정을 커스터마이징할 수 있습니다:

```env
# 서버 설정
HOST=0.0.0.0
PORT=8000

# 크롤링 설정
MAX_CONCURRENT_JOBS=10
MAX_PAGES_PER_JOB=20
RATE_LIMIT_DELAY=0.5

# 파일 설정
DOWNLOAD_DIR=downloads
MAX_FILE_SIZE_MB=50
```

## 🚨 주의사항

1. **robots.txt 준수**: 크롤링 대상 사이트의 robots.txt를 확인하세요
2. **Rate Limiting**: 서버에 부담을 주지 않도록 적절한 딜레이를 설정하세요
3. **저작권**: 수집한 데이터의 저작권을 확인하세요
4. **개인정보**: 개인정보가 포함된 데이터 수집 시 주의하세요

## 📚 API 엔드포인트

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | 메인 대시보드 |
| POST | `/jobs/create` | 새 크롤링 작업 생성 |
| GET | `/jobs/{job_id}/status` | 작업 상태 조회 |
| POST | `/quick-crawl` | 빠른 자동 크롤링 |
| GET | `/downloads/{filename}` | 파일 다운로드 |

## 🐛 문제 해결

### Python을 찾을 수 없음
```bash
# Python 설치 확인
python --version
# 또는
python3 --version

# Python 설치 (macOS)
brew install python3

# Python 설치 (Windows)
# https://www.python.org/downloads/ 에서 다운로드
```

### 포트가 이미 사용 중
```bash
# 8000 포트 사용 프로세스 확인 (macOS/Linux)
lsof -i :8000

# 다른 포트로 실행
uvicorn simple_main:app --port 8001
```

### 권한 오류 (macOS/Linux)
```bash
chmod +x run.sh
```

## 📞 지원

문제가 있거나 기능 요청이 있으시면 이슈를 등록해주세요!

---

Made with ❤️ for 크몽 freelancers