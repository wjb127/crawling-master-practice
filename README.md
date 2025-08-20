# 🕷️ 크롤링 마스터 프랙티스

크몽 프리랜서를 위한 완벽한 웹 크롤링 포트폴리오 및 실습 프로젝트

## 🚀 Quick Start

```bash
# 1. 클론
git clone https://github.com/wjb127/crawling-master-practice.git
cd crawling-master-practice

# 2. 웹 서비스 실행
cd web_crawler_service
./run.sh  # Mac/Linux
# 또는
run.bat   # Windows

# 3. 접속
http://localhost:8000 - 메인 크롤링 서비스
http://localhost:8001 - 포트폴리오 데모
```

## 📚 프로젝트 구조

```
crawling-master-practice/
├── 📖 크몽_크롤링_외주_준비_가이드.md     # 크몽 프리랜서 가이드
├── 📊 크롤링_가능_불가능_영역_가이드.md   # 기술적 한계 설명
├── 📝 PRD_크롤링_툴.md                   # 제품 요구사항 문서
├── 🎨 UI_디자인_가이드.md                # UI/UX 가이드
│
├── 🔧 크롤러 구현체/
│   ├── basic_crawler.py                 # BeautifulSoup 기본
│   ├── dynamic_crawler_simple.py        # Selenium 동적 크롤링
│   ├── advanced_api_crawler.py          # API 직접 호출
│   └── login_crawler.py                 # 로그인/세션 관리
│
└── 🌐 web_crawler_service/              # FastAPI + HTMX 웹서비스
    ├── simple_main.py                   # 메인 서버
    ├── demo_portfolio.py                # 포트폴리오 데모
    ├── test_crawlers.py                 # TDD 테스트
    ├── templates/                       # HTML 템플릿
    ├── requirements.txt                 # 의존성
    └── run.sh / run.bat                # 실행 스크립트
```

## ✨ 주요 기능

### 1. 🎯 원클릭 포트폴리오 데모
- **기본 크롤러**: 네이버 뉴스 실시간 수집
- **API 크롤러**: GitHub 인기 레포지토리
- **비동기 크롤링**: 멀티 사이트 동시 수집
- **스마트 선택자**: AI 기반 자동 감지
- **데이터 정제**: XSS 방지, 표준화

### 2. 🛠️ 프로덕션 레디 웹서비스
- FastAPI 백엔드
- HTMX 실시간 업데이트
- Tailwind CSS 모던 UI
- 엑셀 다운로드
- DB 없는 심플 구조

### 3. 🧪 TDD 테스트 스위트
- 단위 테스트
- 통합 테스트
- 비동기 테스트
- 에러 처리 테스트

## 🎓 학습 로드맵

### 1개월차: 기초
- HTML/CSS 선택자
- BeautifulSoup 마스터
- requests 라이브러리

### 2개월차: 중급
- Selenium 동적 크롤링
- API 리버스 엔지니어링
- 데이터 정제/변환

### 3개월차: 고급
- 비동기 크롤링 (asyncio)
- Anti-bot 우회
- 분산 크롤링

### 4개월차: 실전
- 크몽 포트폴리오 작성
- 가격 책정 전략
- 고객 관리

## 💰 크몽 가격 전략

| 난이도 | 내용 | 가격 |
|--------|------|------|
| 기본 | 정적 사이트 크롤링 | 5-10만원 |
| 중급 | 동적 사이트, 로그인 | 10-30만원 |
| 고급 | API 연동, 대량 수집 | 30-50만원 |
| 프리미엄 | Anti-bot 우회, 실시간 | 50만원+ |

## 🔥 Firecrawl API 비교

### 기존 크롤링 vs Firecrawl

| 항목 | 기존 방식 | Firecrawl |
|------|-----------|-----------|
| JS 렌더링 | Selenium 필요 | ✅ 자동 |
| Anti-bot | 수동 구현 | ✅ 내장 |
| 속도 | 느림 | ⚡ 초고속 |
| 유지보수 | 지속 필요 | ✅ AI 자동 |
| 비용 | 서버+개발 | API 과금 |

## 📋 체크리스트

### 프로젝트 시작 전
- [ ] robots.txt 확인
- [ ] 법적 문제 검토
- [ ] 데이터 용량 예측
- [ ] 크롤링 주기 결정

### 개발 중
- [ ] 에러 처리 구현
- [ ] 로깅 시스템
- [ ] 데이터 검증
- [ ] 성능 최적화

### 납품 시
- [ ] 사용 설명서
- [ ] 유지보수 가이드
- [ ] 테스트 결과
- [ ] 소스코드 전달

## 🚨 주의사항

1. **법적 준수**: 저작권, 개인정보보호법 확인
2. **윤리적 크롤링**: robots.txt 준수, 서버 부하 최소화
3. **데이터 보안**: 크롤링한 데이터 안전 관리
4. **클라이언트 교육**: 가능/불가능 영역 명확히 전달

## 🤝 기여하기

1. Fork 후 개선사항 추가
2. Pull Request 제출
3. 이슈 리포트 환영

## 📄 라이센스

MIT License - 자유롭게 사용하세요!

## 📞 문의

- GitHub Issues: 버그 리포트, 기능 제안
- 크몽 프로필: [링크 추가]

---

**Made with ❤️ for 크몽 Freelancers**

⭐ 도움이 되었다면 Star 부탁드립니다!