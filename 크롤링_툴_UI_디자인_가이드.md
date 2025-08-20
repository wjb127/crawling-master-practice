# 🎨 크롤링 툴 UI 디자인 가이드

## 📐 UI 설계 원칙

### 1. 사용자 중심 디자인
```markdown
✅ 핵심 원칙:
- 기술 모르는 사람도 직관적으로 사용
- 3클릭 이내 모든 기능 접근
- 실시간 피드백 제공
- 에러 시 명확한 안내
```

### 2. 정보 계층 구조
```
1단계: 대시보드 (한눈에 현황 파악)
2단계: 작업 관리 (크롤링 설정)
3단계: 상세 설정 (고급 옵션)
4단계: 결과 분석 (데이터 시각화)
```

---

## 🖥️ UI 레이아웃 구조

### Desktop 레이아웃 (1920x1080)
```
┌─────────────────────────────────────────────────┐
│  🕷️ CrawlMaster Pro    [최소화][최대화][닫기]   │
├──────────┬──────────────────────────────────────┤
│          │                                      │
│  사이드바  │            메인 콘텐츠 영역           │
│          │                                      │
│  - 대시보드│     ┌──────────────────────┐       │
│  - 새작업  │     │   실시간 크롤링 상태    │       │
│  - 작업목록│     └──────────────────────┘       │
│  - 데이터  │                                    │
│  - 설정    │     ┌──────────────────────┐       │
│          │     │    데이터 프리뷰        │       │
│          │     └──────────────────────┘       │
├──────────┴──────────────────────────────────────┤
│  상태바: ✓ 연결됨 | CPU: 45% | 메모리: 2.3GB     │
└─────────────────────────────────────────────────┘
```

### Mobile 레이아웃 (375x812)
```
┌─────────────┐
│  ☰  로고  🔔 │ <- 헤더
├─────────────┤
│             │
│  탭 메뉴     │ <- 스와이프 가능
│ [작업][데이터]│
├─────────────┤
│             │
│  콘텐츠      │ <- 스크롤 영역
│             │
│             │
├─────────────┤
│  플로팅 버튼  │ <- 새 작업 시작
│      (+)     │
└─────────────┘
```

---

## 🎨 디자인 시스템

### 색상 팔레트
```css
/* Primary Colors */
--primary-blue: #2563EB;      /* 메인 액션 */
--primary-dark: #1E40AF;      /* 호버 상태 */
--primary-light: #DBEAFE;     /* 배경 */

/* Status Colors */
--success: #10B981;           /* 성공/완료 */
--warning: #F59E0B;           /* 경고/진행중 */
--error: #EF4444;             /* 에러/실패 */
--info: #3B82F6;              /* 정보 */

/* Neutral Colors */
--gray-900: #111827;          /* 메인 텍스트 */
--gray-600: #4B5563;          /* 서브 텍스트 */
--gray-300: #D1D5DB;          /* 보더 */
--gray-100: #F3F4F6;          /* 배경 */
--white: #FFFFFF;             /* 카드 배경 */
```

### 타이포그래피
```css
/* Font Family */
font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI';

/* Font Sizes */
--text-xs: 12px;      /* 캡션, 라벨 */
--text-sm: 14px;      /* 본문 */
--text-base: 16px;    /* 기본 */
--text-lg: 18px;      /* 서브 헤딩 */
--text-xl: 20px;      /* 헤딩 */
--text-2xl: 24px;     /* 타이틀 */
--text-3xl: 30px;     /* 대시보드 숫자 */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### 컴포넌트 스타일
```css
/* Buttons */
.btn-primary {
  background: var(--primary-blue);
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

/* Cards */
.card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--gray-300);
}

/* Input Fields */
.input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--gray-300);
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.2s;
}

.input:focus {
  outline: none;
  border-color: var(--primary-blue);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}
```

---

## 🔧 주요 UI 컴포넌트

### 1. 대시보드 위젯
```jsx
// 실시간 상태 카드
<StatusCard>
  <StatusIcon status="running" />
  <StatusTitle>크롤링 진행 중</StatusTitle>
  <ProgressBar value={65} max={100} />
  <StatusDetails>
    <Detail label="수집된 데이터" value="1,234개" />
    <Detail label="예상 완료 시간" value="약 5분" />
    <Detail label="에러" value="0개" highlight="success" />
  </StatusDetails>
</StatusCard>
```

### 2. 크롤링 설정 폼
```jsx
// 스텝별 설정 마법사
<SetupWizard>
  <Step1 title="기본 정보">
    <Input label="작업 이름" placeholder="예: 네이버 뉴스 수집" />
    <Input label="대상 URL" placeholder="https://..." />
    <Select label="크롤링 유형">
      <Option>정적 웹사이트</Option>
      <Option>동적 웹사이트 (JavaScript)</Option>
      <Option>API 엔드포인트</Option>
    </Select>
  </Step1>
  
  <Step2 title="데이터 선택">
    <CheckboxGroup label="수집할 데이터">
      <Checkbox>제목</Checkbox>
      <Checkbox>본문</Checkbox>
      <Checkbox>이미지</Checkbox>
      <Checkbox>작성자</Checkbox>
      <Checkbox>날짜</Checkbox>
    </CheckboxGroup>
  </Step2>
  
  <Step3 title="고급 설정">
    <NumberInput label="페이지 수" min={1} max={1000} />
    <NumberInput label="딜레이(초)" min={0.5} max={10} />
    <Toggle label="프록시 사용" />
    <Toggle label="쿠키 저장" />
  </Step3>
</SetupWizard>
```

### 3. 데이터 테이블
```jsx
// 결과 데이터 테이블
<DataTable>
  <TableHeader>
    <Column sortable>제목</Column>
    <Column sortable>URL</Column>
    <Column>상태</Column>
    <Column sortable>수집 시간</Column>
    <Column>액션</Column>
  </TableHeader>
  
  <TableBody>
    {data.map(item => (
      <TableRow key={item.id}>
        <Cell>{item.title}</Cell>
        <Cell><Link href={item.url}>링크</Link></Cell>
        <Cell><StatusBadge status={item.status} /></Cell>
        <Cell>{formatDate(item.crawledAt)}</Cell>
        <Cell>
          <ActionButtons>
            <IconButton icon="view" />
            <IconButton icon="download" />
            <IconButton icon="delete" />
          </ActionButtons>
        </Cell>
      </TableRow>
    ))}
  </TableBody>
  
  <TableFooter>
    <Pagination 
      currentPage={1} 
      totalPages={10}
      onPageChange={handlePageChange}
    />
  </TableFooter>
</DataTable>
```

### 4. 실시간 로그 뷰어
```jsx
// 실시간 로그 스트림
<LogViewer>
  <LogHeader>
    <LogTitle>실시간 로그</LogTitle>
    <LogActions>
      <Button size="sm" onClick={clearLogs}>Clear</Button>
      <Button size="sm" onClick={downloadLogs}>Download</Button>
    </LogActions>
  </LogHeader>
  
  <LogContent>
    {logs.map((log, index) => (
      <LogEntry key={index} level={log.level}>
        <LogTime>{log.timestamp}</LogTime>
        <LogLevel level={log.level}>{log.level}</LogLevel>
        <LogMessage>{log.message}</LogMessage>
      </LogEntry>
    ))}
  </LogContent>
  
  <LogFooter>
    <AutoScroll enabled={true} />
    <LogFilter levels={['info', 'warning', 'error']} />
  </LogFooter>
</LogViewer>
```

---

## 📱 반응형 디자인

### Breakpoints
```css
/* Mobile First Approach */
/* Mobile: 320px - 768px */
@media (min-width: 320px) {
  .container { padding: 16px; }
  .grid { grid-template-columns: 1fr; }
}

/* Tablet: 768px - 1024px */
@media (min-width: 768px) {
  .container { padding: 24px; }
  .grid { grid-template-columns: repeat(2, 1fr); }
}

/* Desktop: 1024px - 1920px */
@media (min-width: 1024px) {
  .container { padding: 32px; }
  .grid { grid-template-columns: repeat(3, 1fr); }
}

/* Large Desktop: 1920px+ */
@media (min-width: 1920px) {
  .container { max-width: 1440px; margin: 0 auto; }
  .grid { grid-template-columns: repeat(4, 1fr); }
}
```

---

## 🎭 인터랙션 & 애니메이션

### 마이크로 인터랙션
```css
/* 버튼 클릭 피드백 */
@keyframes buttonPress {
  0% { transform: scale(1); }
  50% { transform: scale(0.95); }
  100% { transform: scale(1); }
}

.btn:active {
  animation: buttonPress 0.1s ease-out;
}

/* 로딩 스피너 */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spinner {
  animation: spin 1s linear infinite;
}

/* 진행 바 애니메이션 */
.progress-bar {
  transition: width 0.3s ease-out;
  background: linear-gradient(
    90deg,
    #2563EB 0%,
    #3B82F6 50%,
    #2563EB 100%
  );
  background-size: 200% 100%;
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
```

### 페이지 전환
```javascript
// Framer Motion 예제
const pageVariants = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 }
};

const pageTransition = {
  type: "tween",
  ease: "easeInOut",
  duration: 0.3
};
```

---

## 🔔 알림 & 피드백

### Toast 알림
```jsx
// 성공 알림
toast.success('크롤링이 완료되었습니다!', {
  duration: 4000,
  position: 'top-right',
  icon: '✅',
  style: {
    background: '#10B981',
    color: 'white',
  },
});

// 에러 알림
toast.error('URL이 유효하지 않습니다', {
  duration: 5000,
  position: 'top-center',
  icon: '❌',
  action: {
    label: '다시 시도',
    onClick: () => retry()
  }
});
```

### 모달 다이얼로그
```jsx
<Modal isOpen={isOpen} onClose={handleClose}>
  <ModalHeader>
    <ModalTitle>크롤링 설정</ModalTitle>
    <CloseButton onClick={handleClose} />
  </ModalHeader>
  
  <ModalBody>
    {/* 폼 내용 */}
  </ModalBody>
  
  <ModalFooter>
    <Button variant="ghost" onClick={handleClose}>
      취소
    </Button>
    <Button variant="primary" onClick={handleSave}>
      저장
    </Button>
  </ModalFooter>
</Modal>
```

---

## 📊 데이터 시각화

### 차트 컴포넌트
```jsx
// 실시간 진행 상황 차트
<LineChart
  data={progressData}
  width={600}
  height={300}
  margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
>
  <CartesianGrid strokeDasharray="3 3" />
  <XAxis dataKey="time" />
  <YAxis />
  <Tooltip />
  <Legend />
  <Line 
    type="monotone" 
    dataKey="collected" 
    stroke="#2563EB" 
    strokeWidth={2}
  />
  <Line 
    type="monotone" 
    dataKey="errors" 
    stroke="#EF4444" 
    strokeWidth={2}
  />
</LineChart>

// 통계 카드
<StatCard>
  <StatIcon>📊</StatIcon>
  <StatValue>12,345</StatValue>
  <StatLabel>총 수집 데이터</StatLabel>
  <StatChange positive>
    <TrendIcon>↑</TrendIcon>
    <span>12% 증가</span>
  </StatChange>
</StatCard>
```

---

## 🌙 다크 모드

### CSS 변수 활용
```css
/* Light Mode (Default) */
:root {
  --bg-primary: #FFFFFF;
  --bg-secondary: #F3F4F6;
  --text-primary: #111827;
  --text-secondary: #4B5563;
  --border: #D1D5DB;
}

/* Dark Mode */
[data-theme="dark"] {
  --bg-primary: #1F2937;
  --bg-secondary: #111827;
  --text-primary: #F9FAFB;
  --text-secondary: #9CA3AF;
  --border: #374151;
}

/* 자동 적용 */
body {
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: background 0.3s, color 0.3s;
}
```

### 토글 스위치
```jsx
<ThemeToggle>
  <ToggleTrack>
    <SunIcon active={theme === 'light'} />
    <MoonIcon active={theme === 'dark'} />
    <ToggleThumb position={theme} />
  </ToggleTrack>
</ThemeToggle>
```

---

## ♿ 접근성 고려사항

### WCAG 2.1 준수
```html
<!-- 키보드 네비게이션 -->
<button 
  tabindex="0"
  role="button"
  aria-label="크롤링 시작"
  aria-pressed="false"
  onKeyDown={handleKeyDown}
>
  시작
</button>

<!-- 스크린 리더 지원 -->
<div role="status" aria-live="polite" aria-atomic="true">
  <span class="sr-only">
    크롤링 진행률: 65%
  </span>
</div>

<!-- 폼 접근성 -->
<label for="url-input">
  대상 URL
  <span aria-label="required">*</span>
</label>
<input 
  id="url-input"
  type="url"
  required
  aria-describedby="url-error"
/>
<span id="url-error" role="alert">
  유효한 URL을 입력해주세요
</span>
```

---

## 🚀 성능 최적화

### 레이지 로딩
```jsx
// 컴포넌트 레이지 로딩
const DataTable = lazy(() => import('./components/DataTable'));
const ChartView = lazy(() => import('./components/ChartView'));

// 이미지 레이지 로딩
<img 
  loading="lazy"
  src="placeholder.jpg"
  data-src="actual-image.jpg"
  onLoad={handleImageLoad}
/>
```

### 가상 스크롤
```jsx
// react-window 활용
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={10000}
  itemSize={50}
  width={'100%'}
>
  {({ index, style }) => (
    <div style={style}>
      Row {index}
    </div>
  )}
</FixedSizeList>
```

---

## 📱 플랫폼별 UI

### Electron (Desktop App)
```javascript
// 네이티브 메뉴바
const menuTemplate = [
  {
    label: '파일',
    submenu: [
      { label: '새 작업', accelerator: 'CmdOrCtrl+N' },
      { label: '열기', accelerator: 'CmdOrCtrl+O' },
      { type: 'separator' },
      { label: '종료', role: 'quit' }
    ]
  }
];

// 시스템 트레이
const tray = new Tray('icon.png');
const contextMenu = Menu.buildFromTemplate([
  { label: '대시보드 열기' },
  { label: '일시정지' },
  { label: '종료' }
]);
tray.setContextMenu(contextMenu);
```

### PWA (Progressive Web App)
```json
// manifest.json
{
  "name": "CrawlMaster Pro",
  "short_name": "CrawlMaster",
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#2563EB",
  "background_color": "#FFFFFF",
  "icons": [
    {
      "src": "icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    }
  ]
}
```

---

## 🎯 UI/UX 체크리스트

### 개발 전
- [ ] 사용자 페르소나 정의
- [ ] 유저 플로우 다이어그램
- [ ] 와이어프레임 작성
- [ ] 디자인 시스템 구축
- [ ] 프로토타입 제작

### 개발 중
- [ ] 반응형 디자인 구현
- [ ] 다크 모드 지원
- [ ] 키보드 단축키
- [ ] 로딩 상태 표시
- [ ] 에러 처리 UI

### 개발 후
- [ ] 사용성 테스트
- [ ] 접근성 검사
- [ ] 성능 측정
- [ ] 크로스 브라우저 테스트
- [ ] 사용자 피드백 수집

---

*이 가이드는 실제 크롤링 툴 UI 개발 경험을 바탕으로 작성되었습니다.*