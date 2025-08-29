# 🎯 CSS 선택자 완벽 치트시트

## 📌 크롤링 마스터에서 바로 사용 가능한 선택자 모음

---

## 🔰 초급 - 기본 선택자

### 1. 태그 선택자
```css
/* 모든 제목 선택 */
h1              /* 큰 제목 */
h2              /* 중간 제목 */
p               /* 문단 */
div             /* 구역 */
span            /* 인라인 텍스트 */
a               /* 링크 */
img             /* 이미지 */
```

### 2. 클래스 선택자 (점 .)
```css
.title          /* class="title" */
.content        /* class="content" */
.price          /* class="price" */
.author         /* class="author" */
```

### 3. ID 선택자 (샵 #)
```css
#header         /* id="header" */
#main           /* id="main" */
#footer         /* id="footer" */
```

---

## 🏆 중급 - 조합 선택자

### 1. 자손 선택자 (공백)
```css
/* article 안의 모든 p 태그 */
article p

/* 실전 예시 */
.news-list .title       /* 뉴스 목록의 제목 */
div.container h2        /* 컨테이너 안의 h2 */
#content .author        /* content 영역의 작성자 */
```

### 2. 직계 자식 선택자 (>)
```css
/* ul의 직접 자식 li만 */
ul > li

/* 실전 예시 */
.menu > li              /* 메뉴의 1단계 항목만 */
article > p             /* article 바로 아래 p만 */
div.post > h2           /* post의 직접 제목만 */
```

### 3. 인접 형제 선택자 (+)
```css
/* h1 바로 다음의 p */
h1 + p

/* 실전 예시 */
.title + .date          /* 제목 다음의 날짜 */
h2 + .summary          /* 제목 다음의 요약 */
```

### 4. 일반 형제 선택자 (~)
```css
/* h1 이후의 모든 p */
h1 ~ p

/* 실전 예시 */
.header ~ .content      /* 헤더 이후 모든 콘텐츠 */
```

---

## 🚀 고급 - 속성 선택자

### 1. 속성 존재 확인
```css
[href]          /* href 속성이 있는 모든 요소 */
[target]        /* target 속성이 있는 요소 */
img[alt]        /* alt 속성이 있는 이미지 */
```

### 2. 속성 값 일치
```css
[type="text"]           /* type이 정확히 "text" */
[class="highlight"]     /* class가 정확히 "highlight" */
a[target="_blank"]      /* 새 창으로 열리는 링크 */
```

### 3. 부분 일치
```css
/* 시작 부분 일치 */
[href^="https://"]      /* https로 시작하는 링크 */
[src^="/images/"]       /* /images/로 시작하는 이미지 */

/* 끝 부분 일치 */
[href$=".pdf"]          /* PDF 파일 링크 */
[src$=".jpg"]           /* JPG 이미지 */

/* 포함 */
[href*="naver"]         /* naver가 포함된 링크 */
[class*="btn"]          /* btn이 포함된 클래스 */
```

---

## 💎 전문가 - 가상 선택자

### 1. 위치 기반 선택자
```css
/* 첫 번째/마지막 */
li:first-child          /* 첫 번째 li */
li:last-child           /* 마지막 li */

/* n번째 */
li:nth-child(2)         /* 2번째 li */
li:nth-child(odd)       /* 홀수 번째 */
li:nth-child(even)      /* 짝수 번째 */
li:nth-child(3n)        /* 3의 배수 */

/* 타입별 n번째 */
p:nth-of-type(2)        /* 2번째 p 태그 */
h2:first-of-type        /* 첫 번째 h2 */
```

### 2. 콘텐츠 기반 선택자
```css
/* 텍스트 포함 (jQuery 스타일) */
:contains("원")         /* "원" 텍스트 포함 */
:has(img)              /* 이미지를 포함한 요소 */
:empty                 /* 비어있는 요소 */
```

### 3. 부정 선택자
```css
:not(.ad)              /* ad 클래스가 아닌 것 */
p:not(:empty)          /* 비어있지 않은 p */
a:not([target])        /* target 속성이 없는 링크 */
```

---

## 🌐 사이트별 실전 선택자

### 📰 네이버 뉴스
```css
/* 기사 제목 */
.sa_text_title

/* 기사 내용 */
.sa_text_lede

/* 기사 날짜 */
.sa_text_datetime

/* 기사 이미지 */
.sa_thumb img

/* 기사 링크 */
.sa_text a[href]
```

### 📝 네이버 블로그
```css
/* 포스트 제목 */
.se-title-text

/* 포스트 내용 */
.se-main-container

/* 작성 날짜 */
.se_publishDate

/* 태그 */
.blog_tag
```

### 🛒 쿠팡
```css
/* 상품명 */
.name

/* 가격 */
.price-value

/* 별점 */
.rating

/* 리뷰 수 */
.rating-total-count

/* 배송 정보 */
.badge.rocket
```

### 📺 유튜브
```css
/* 동영상 제목 */
#video-title

/* 채널명 */
.ytd-channel-name

/* 조회수 */
.view-count

/* 업로드 날짜 */
#date-text
```

---

## 🎨 패턴별 선택자

### 1. 리스트/목록
```css
/* 일반 목록 */
ul li
ol li
.list-item

/* 그리드 형태 */
.grid-item
.card
.product-item
```

### 2. 테이블
```css
/* 테이블 헤더 */
table thead th

/* 테이블 데이터 */
table tbody td

/* 특정 열 */
td:nth-child(2)        /* 2번째 열 */
```

### 3. 폼 요소
```css
/* 입력 필드 */
input[type="text"]
input[type="email"]
textarea

/* 버튼 */
button
input[type="submit"]
.btn, .button
```

### 4. 미디어
```css
/* 이미지 */
img
.thumbnail img
picture img

/* 비디오 */
video
iframe[src*="youtube"]
```

---

## 🔧 복합 선택자 실전 예제

### 예제 1: 뉴스 기사 크롤링
```css
제목: article h2.title
작성자: article .author-name
날짜: article time[datetime]
내용: article .content p
이미지: article img.featured
태그: article .tags span
```

### 예제 2: 쇼핑몰 상품
```css
상품명: .product-list .name
가격: .product-list .price:not(.before)
할인율: .product-list .discount-rate
평점: .product-list .rating-star
리뷰: .product-list .review-count
배송: .product-list .delivery-badge
```

### 예제 3: 블로그 포스트
```css
제목: .post-header h1
부제목: .post-header .subtitle
작성일: .post-meta time
카테고리: .post-meta .category
본문: .post-content > p
인용구: .post-content blockquote
코드: .post-content pre code
```

---

## 🎯 트러블슈팅

### 선택자가 작동하지 않을 때

#### 1. 동적 로딩 확인
```css
/* 잘못된 예 */
.content  /* JavaScript로 나중에 로딩됨 */

/* 해결책 */
지연 시간을 2-3초로 늘리기
```

#### 2. 프레임/아이프레임
```css
/* iframe 내부 요소는 직접 선택 불가 */
iframe 내부 콘텐츠는 별도 URL로 접근
```

#### 3. 클래스명 변경
```css
/* 동적 클래스명 */
.css-1x2y3z  /* 빌드마다 변경됨 */

/* 해결책: 부분 일치 사용 */
[class*="title"]
[class^="price-"]
```

---

## 💡 프로 팁

### 1. 선택자 최적화
```css
/* 느림 */
body > div > div > ul > li > a

/* 빠름 */
.menu-link
```

### 2. 안정적인 선택자
```css
/* 불안정 (구조 의존) */
div:nth-child(3) > p:first-child

/* 안정적 (의미 기반) */
.article-content
```

### 3. 대체 선택자 준비
```css
/* 주 선택자 */
.price-now

/* 대체 선택자 */
.price, .cost, [class*="price"]
```

---

## 📊 선택자 우선순위

1. **ID** (#id) - 가장 높음
2. **클래스** (.class)
3. **속성** ([attr])
4. **가상** (:pseudo)
5. **태그** (tag) - 가장 낮음

---

## 🔍 디버깅 도구

### 브라우저 개발자 도구
1. `F12` 키 누르기
2. Elements 탭 선택
3. 원하는 요소 우클릭
4. Copy → Copy selector

### 선택자 테스트
```javascript
// 브라우저 콘솔에서 테스트
document.querySelectorAll('.your-selector').length
```

---

## 📝 체크리스트

크롤링 전 확인사항:
- [ ] 선택자가 unique한가?
- [ ] 동적 로딩 요소인가?
- [ ] 여러 페이지에서 동일한가?
- [ ] 대체 선택자가 있는가?
- [ ] 너무 복잡하지 않은가?

---

**마지막 팁**: 가장 간단한 선택자가 가장 좋은 선택자입니다! 🎯

© 2024 크롤링 마스터 | CSS 선택자 마스터 가이드