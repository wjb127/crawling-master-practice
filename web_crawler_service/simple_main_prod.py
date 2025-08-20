#!/usr/bin/env python3
"""
프로덕션용 FastAPI + HTMX 크롤링 서비스
Fly.io 배포에 최적화된 버전
"""

import os
from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, List, Any
from enum import Enum
from pathlib import Path
from urllib.parse import urlparse, urljoin
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
from io import BytesIO

# ==================== 프로덕션 설정 ====================
# 환경변수에서 설정 읽기
PORT = int(os.getenv("PORT", "8080"))
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", "20"))
MAX_PAGES_PER_JOB = int(os.getenv("MAX_PAGES_PER_JOB", "50"))
RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", "0.5"))

class CrawlStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class CrawlJob:
    def __init__(self, name: str, url: str, selectors: Dict[str, str]):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.url = url
        self.selectors = selectors
        self.status = CrawlStatus.PENDING
        self.progress = 0
        self.total_items = 0
        self.collected_items = 0
        self.created_at = datetime.now()
        self.result_file = None
        self.data = []
        self.logs = []


# ==================== 앱 초기화 ====================
app = FastAPI(
    title="Crawling Master Service",
    description="프로덕션 크롤링 서비스",
    version="1.0.0"
)

templates = Jinja2Templates(directory="templates")

# 전역 저장소 (메모리) - 프로덕션에서는 Redis 권장
jobs_store: Dict[str, CrawlJob] = {}

# 디렉토리 생성
Path("templates").mkdir(exist_ok=True)
Path("downloads").mkdir(exist_ok=True)
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")


# ==================== 크롤러 엔진 ====================
class SimpleCrawler:
    """프로덕션용 비동기 크롤러"""
    
    def __init__(self, job: CrawlJob):
        self.job = job
        self.session = None
        
    async def crawl(self):
        """크롤링 실행"""
        try:
            self.job.status = CrawlStatus.RUNNING
            self.log(f"🚀 크롤링 시작: {self.job.url}")
            
            # 타임아웃과 헤더 설정
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as self.session:
                # 메인 페이지 크롤링
                html = await self.fetch_page(self.job.url)
                if not html:
                    raise Exception("페이지를 가져올 수 없습니다")
                
                # 데이터 추출
                soup = BeautifulSoup(html, 'html.parser')
                
                # 선택자별로 데이터 추출
                main_data = {}
                for field, selector in self.job.selectors.items():
                    try:
                        elements = soup.select(selector)
                        if elements:
                            if len(elements) > 1:
                                main_data[field] = [el.get_text(strip=True) for el in elements[:10]]
                            else:
                                main_data[field] = elements[0].get_text(strip=True)
                        else:
                            main_data[field] = ""
                    except Exception as e:
                        main_data[field] = f"Error: {str(e)}"
                        self.log(f"⚠️ {field} 추출 실패: {str(e)}")
                
                main_data['url'] = self.job.url
                main_data['crawled_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.job.data.append(main_data)
                
                # 추가 페이지 찾기 (프로덕션: 제한된 수만)
                links = self.find_similar_links(soup, self.job.url)
                max_pages = min(len(links), MAX_PAGES_PER_JOB)
                self.job.total_items = max_pages + 1
                
                # 제한된 수의 추가 페이지만 크롤링
                for idx, link in enumerate(links[:max_pages], 1):
                    self.job.progress = int((idx / (max_pages + 1)) * 100)
                    self.log(f"📄 페이지 {idx}/{max_pages} 크롤링 중...")
                    
                    page_html = await self.fetch_page(link)
                    if page_html:
                        page_soup = BeautifulSoup(page_html, 'html.parser')
                        page_data = {}
                        
                        for field, selector in self.job.selectors.items():
                            try:
                                elements = page_soup.select(selector)
                                if elements:
                                    page_data[field] = elements[0].get_text(strip=True)
                                else:
                                    page_data[field] = ""
                            except:
                                page_data[field] = ""
                        
                        page_data['url'] = link
                        page_data['crawled_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        self.job.data.append(page_data)
                        self.job.collected_items += 1
                    
                    await asyncio.sleep(RATE_LIMIT_DELAY)  # Rate limiting
                
                # 엑셀 파일 생성
                if self.job.data:
                    self.save_to_excel()
                
                self.job.status = CrawlStatus.COMPLETED
                self.job.progress = 100
                self.log(f"✅ 크롤링 완료! {len(self.job.data)}개 항목 수집")
                
        except Exception as e:
            self.job.status = CrawlStatus.FAILED
            self.log(f"❌ 크롤링 실패: {str(e)}")
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """페이지 가져오기"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    self.log(f"HTTP {response.status}: {url}")
                    return None
        except Exception as e:
            self.log(f"페이지 로드 실패: {url} - {str(e)}")
            return None
    
    def find_similar_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """유사한 링크 찾기"""
        links = []
        parsed_base = urlparse(base_url)
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            # 절대 URL로 변환
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            
            # 같은 도메인의 링크만
            if parsed.netloc == parsed_base.netloc:
                if full_url not in links and full_url != base_url:
                    links.append(full_url)
        
        return links[:MAX_PAGES_PER_JOB]  # 프로덕션: 제한
    
    def save_to_excel(self):
        """엑셀 파일로 저장"""
        if not self.job.data:
            return
        
        df = pd.DataFrame(self.job.data)
        
        # 파일명 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.job.name.replace(' ', '_')}_{timestamp}.xlsx"
        filepath = Path("downloads") / filename
        
        # 스타일 적용하여 저장
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='크롤링 결과')
            
            # 스타일 적용
            workbook = writer.book
            worksheet = writer.sheets['크롤링 결과']
            
            # 헤더 스타일
            header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
            header_font = Font(color='FFFFFF', bold=True)
            
            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center')
            
            # 열 너비 자동 조정
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
        
        self.job.result_file = filename
        self.log(f"💾 파일 저장 완료: {filename}")
    
    def log(self, message: str):
        """로그 기록"""
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] {message}"
        self.job.logs.append(log_entry)
        if ENVIRONMENT != "production":
            print(log_entry)


# ==================== 헬퍼 함수 ====================
def auto_detect_selectors(html: str) -> Dict[str, str]:
    """HTML에서 자동으로 선택자 감지"""
    soup = BeautifulSoup(html, 'html.parser')
    selectors = {}
    
    # 제목 패턴
    title_patterns = ['h1', 'h2', '.title', '.headline', '[class*="title"]', '[class*="heading"]']
    for pattern in title_patterns:
        if soup.select(pattern):
            selectors['title'] = pattern
            break
    
    # 내용 패턴
    content_patterns = ['article', '.content', '.body', 'main', '.post-content', '[class*="content"]']
    for pattern in content_patterns:
        if soup.select(pattern):
            selectors['content'] = pattern
            break
    
    # 날짜 패턴
    date_patterns = ['time', '.date', '.timestamp', '[datetime]', '[class*="date"]']
    for pattern in date_patterns:
        if soup.select(pattern):
            selectors['date'] = pattern
            break
    
    # 이미지
    if soup.select('img'):
        selectors['images'] = 'img'
    
    # 링크
    if soup.select('a[href]'):
        selectors['links'] = 'a[href]'
    
    return selectors


# ==================== API 라우트 ====================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """메인 페이지"""
    # 활성 작업 수 계산
    active_jobs = sum(1 for job in jobs_store.values() if job.status == CrawlStatus.RUNNING)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "jobs": list(jobs_store.values()),
        "active_jobs": active_jobs,
        "max_jobs": MAX_CONCURRENT_JOBS,
        "environment": ENVIRONMENT
    })


@app.post("/jobs/create", response_class=HTMLResponse)
async def create_job(
    request: Request,
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    url: str = Form(...),
    selectors: str = Form(...)
):
    """새 크롤링 작업 생성"""
    
    # 동시 실행 제한 체크
    running_jobs = sum(1 for job in jobs_store.values() if job.status == CrawlStatus.RUNNING)
    if running_jobs >= MAX_CONCURRENT_JOBS:
        return HTMLResponse(
            content=f'<div class="text-red-500">⚠️ 동시 실행 가능한 작업 수({MAX_CONCURRENT_JOBS})를 초과했습니다.</div>'
        )
    
    # 선택자 파싱
    selector_dict = {}
    for line in selectors.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            selector_dict[key.strip()] = value.strip()
    
    # 작업 생성
    job = CrawlJob(name=name, url=url, selectors=selector_dict)
    jobs_store[job.id] = job
    
    # 백그라운드에서 크롤링 실행
    crawler = SimpleCrawler(job)
    background_tasks.add_task(crawler.crawl)
    
    # 작업 카드 HTML 반환 (HTMX용)
    return templates.TemplateResponse("partials/job_card.html", {
        "request": request,
        "job": job
    })


@app.get("/jobs/{job_id}/status", response_class=HTMLResponse)
async def get_job_status(request: Request, job_id: str):
    """작업 상태 조회 (HTMX polling용)"""
    job = jobs_store.get(job_id)
    if not job:
        return HTMLResponse(content="작업을 찾을 수 없습니다")
    
    return templates.TemplateResponse("partials/job_status.html", {
        "request": request,
        "job": job
    })


@app.post("/quick-crawl", response_class=HTMLResponse)
async def quick_crawl(
    request: Request,
    background_tasks: BackgroundTasks,
    url: str = Form(...)
):
    """빠른 자동 크롤링"""
    
    # URL로 간단한 HTML 가져오기
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
        
        # 자동 선택자 감지
        selectors = auto_detect_selectors(html)
        
        if not selectors:
            return HTMLResponse(
                content='<div class="text-yellow-500">⚠️ 자동 감지된 선택자가 없습니다. 수동으로 입력해주세요.</div>'
            )
        
        # 작업 생성
        job = CrawlJob(name=f"자동_{urlparse(url).netloc}", url=url, selectors=selectors)
        jobs_store[job.id] = job
        
        # 크롤링 실행
        crawler = SimpleCrawler(job)
        background_tasks.add_task(crawler.crawl)
        
        return templates.TemplateResponse("partials/job_card.html", {
            "request": request,
            "job": job
        })
        
    except Exception as e:
        return HTMLResponse(
            content=f'<div class="text-red-500">❌ 오류: {str(e)}</div>'
        )


@app.get("/downloads/{filename}")
async def download_file(filename: str):
    """파일 다운로드"""
    file_path = Path("downloads") / filename
    if file_path.exists():
        return FileResponse(
            path=file_path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=filename
        )
    return HTMLResponse(content="파일을 찾을 수 없습니다", status_code=404)


@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {
        "status": "healthy",
        "environment": ENVIRONMENT,
        "active_jobs": sum(1 for job in jobs_store.values() if job.status == CrawlStatus.RUNNING),
        "total_jobs": len(jobs_store)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)