#!/usr/bin/env python3
"""
FastAPI + HTMX + Tailwind 크롤링 웹서비스
실시간 크롤링 작업 관리 및 모니터링
"""

from fastapi import FastAPI, Request, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import os
from pathlib import Path
import pandas as pd
from urllib.parse import urlparse, urljoin
import hashlib
import redis.asyncio as redis
from pydantic import BaseModel, HttpUrl


# ==================== 설정 ====================
class CrawlStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CrawlJob(BaseModel):
    id: str
    name: str
    url: HttpUrl
    selectors: Dict[str, str]
    status: CrawlStatus = CrawlStatus.PENDING
    progress: int = 0
    total_items: int = 0
    collected_items: int = 0
    error_count: int = 0
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_file: Optional[str] = None
    logs: List[str] = []


# ==================== 앱 초기화 ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시
    app.state.redis = await redis.from_url("redis://localhost:6379", decode_responses=True)
    app.state.jobs = {}  # 메모리 저장소 (실제로는 DB 사용)
    app.state.crawlers = {}  # 활성 크롤러
    
    # 디렉토리 생성
    Path("static").mkdir(exist_ok=True)
    Path("downloads").mkdir(exist_ok=True)
    Path("templates").mkdir(exist_ok=True)
    
    yield
    
    # 종료 시
    await app.state.redis.close()
    
    # 활성 크롤러 정리
    for crawler in app.state.crawlers.values():
        if hasattr(crawler, 'cancel'):
            crawler.cancel()


app = FastAPI(title="CrawlMaster Pro", lifespan=lifespan)
templates = Jinja2Templates(directory="templates")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")


# ==================== 크롤러 엔진 ====================
class AsyncCrawler:
    """비동기 크롤러 엔진"""
    
    def __init__(self, job_id: str, app):
        self.job_id = job_id
        self.app = app
        self.session = None
        self.cancelled = False
        
    async def crawl(self, job: CrawlJob):
        """크롤링 실행"""
        try:
            job.status = CrawlStatus.RUNNING
            job.started_at = datetime.now()
            await self.log(f"크롤링 시작: {job.url}")
            
            async with aiohttp.ClientSession() as self.session:
                # 메인 페이지 크롤링
                html = await self.fetch_page(str(job.url))
                if not html:
                    raise Exception("페이지를 가져올 수 없습니다")
                
                # 데이터 추출
                data = await self.extract_data(html, job.selectors)
                
                # 링크 수집 (페이지네이션)
                links = await self.find_links(html, str(job.url))
                job.total_items = len(links) + 1
                
                # 추가 페이지 크롤링
                all_data = [data]
                for idx, link in enumerate(links[:20], 1):  # 최대 20페이지
                    if self.cancelled:
                        break
                        
                    await self.log(f"페이지 {idx}/{len(links)} 크롤링 중...")
                    job.progress = int((idx / job.total_items) * 100)
                    
                    page_html = await self.fetch_page(link)
                    if page_html:
                        page_data = await self.extract_data(page_html, job.selectors)
                        if page_data:
                            all_data.append(page_data)
                            job.collected_items += 1
                    
                    await asyncio.sleep(1)  # Rate limiting
                
                # 결과 저장
                result_file = await self.save_results(all_data, job)
                job.result_file = result_file
                
                job.status = CrawlStatus.COMPLETED
                job.completed_at = datetime.now()
                job.progress = 100
                await self.log(f"크롤링 완료: {len(all_data)}개 항목 수집")
                
        except Exception as e:
            job.status = CrawlStatus.FAILED
            job.error_count += 1
            await self.log(f"크롤링 실패: {str(e)}")
            
    async def fetch_page(self, url: str) -> Optional[str]:
        """페이지 가져오기"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
        except Exception as e:
            await self.log(f"페이지 요청 실패: {str(e)}")
        return None
    
    async def extract_data(self, html: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """데이터 추출"""
        soup = BeautifulSoup(html, 'html.parser')
        data = {}
        
        for field, selector in selectors.items():
            try:
                if selector.startswith('//'):  # XPath는 지원 안함
                    continue
                    
                elements = soup.select(selector)
                if elements:
                    # 텍스트 추출
                    if len(elements) == 1:
                        data[field] = elements[0].get_text(strip=True)
                    else:
                        data[field] = [el.get_text(strip=True) for el in elements]
                else:
                    data[field] = None
            except Exception as e:
                data[field] = f"Error: {str(e)}"
                
        data['crawled_at'] = datetime.now().isoformat()
        return data
    
    async def find_links(self, html: str, base_url: str) -> List[str]:
        """링크 찾기 (페이지네이션 등)"""
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        
        # 일반적인 페이지네이션 패턴
        for a in soup.find_all('a', href=True):
            href = a['href']
            # 상대 URL을 절대 URL로 변환
            full_url = urljoin(base_url, href)
            
            # 같은 도메인인지 확인
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                links.add(full_url)
        
        return list(links)[:50]  # 최대 50개
    
    async def save_results(self, data: List[Dict], job: CrawlJob) -> str:
        """결과 저장"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{job.name.replace(' ', '_')}_{timestamp}"
        
        # JSON 저장
        json_path = f"downloads/{filename}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        # CSV 저장
        if data:
            df = pd.DataFrame(data)
            csv_path = f"downloads/{filename}.csv"
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        return filename
    
    async def log(self, message: str):
        """로그 추가"""
        job = self.app.state.jobs.get(self.job_id)
        if job:
            timestamp = datetime.now().strftime('%H:%M:%S')
            job.logs.append(f"[{timestamp}] {message}")
            
            # Redis pub/sub로 실시간 알림
            await self.app.state.redis.publish(
                f"job:{self.job_id}",
                json.dumps({
                    'type': 'log',
                    'message': message,
                    'timestamp': timestamp
                })
            )
    
    def cancel(self):
        """크롤링 취소"""
        self.cancelled = True


# ==================== API 엔드포인트 ====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """메인 페이지"""
    jobs = list(app.state.jobs.values())
    jobs.sort(key=lambda x: x.created_at, reverse=True)
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "jobs": jobs,
            "active_count": sum(1 for j in jobs if j.status == CrawlStatus.RUNNING),
            "completed_count": sum(1 for j in jobs if j.status == CrawlStatus.COMPLETED),
            "total_collected": sum(j.collected_items for j in jobs)
        }
    )


@app.post("/jobs/create", response_class=HTMLResponse)
async def create_job(
    request: Request,
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    url: str = Form(...),
    selectors: str = Form(...)
):
    """새 크롤링 작업 생성"""
    
    # 선택자 파싱
    selector_dict = {}
    for line in selectors.strip().split('\n'):
        if ':' in line:
            field, selector = line.split(':', 1)
            selector_dict[field.strip()] = selector.strip()
    
    # Job 생성
    job = CrawlJob(
        id=str(uuid.uuid4()),
        name=name,
        url=url,
        selectors=selector_dict,
        created_at=datetime.now()
    )
    
    app.state.jobs[job.id] = job
    
    # 백그라운드에서 크롤링 시작
    crawler = AsyncCrawler(job.id, app)
    app.state.crawlers[job.id] = crawler
    background_tasks.add_task(crawler.crawl, job)
    
    # HTMX용 작업 카드 반환
    return f"""
    <div id="job-{job.id}" 
         class="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500"
         hx-get="/jobs/{job.id}/status"
         hx-trigger="every 1s"
         hx-swap="outerHTML">
        <div class="flex justify-between items-start mb-4">
            <div>
                <h3 class="text-lg font-semibold">{job.name}</h3>
                <p class="text-sm text-gray-500">{job.url}</p>
            </div>
            <span class="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm">
                {job.status.value}
            </span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
            <div class="bg-blue-500 h-2 rounded-full transition-all duration-300" 
                 style="width: 0%"></div>
        </div>
        <div class="mt-2 text-sm text-gray-600">
            준비 중...
        </div>
    </div>
    """


@app.get("/jobs/{job_id}/status", response_class=HTMLResponse)
async def get_job_status(job_id: str):
    """작업 상태 조회 (HTMX polling)"""
    job = app.state.jobs.get(job_id)
    if not job:
        return "<div>작업을 찾을 수 없습니다</div>"
    
    # 상태별 색상
    status_colors = {
        CrawlStatus.PENDING: "bg-gray-100 text-gray-800",
        CrawlStatus.RUNNING: "bg-blue-100 text-blue-800",
        CrawlStatus.COMPLETED: "bg-green-100 text-green-800",
        CrawlStatus.FAILED: "bg-red-100 text-red-800",
        CrawlStatus.CANCELLED: "bg-gray-100 text-gray-800"
    }
    
    # 진행 중이 아니면 polling 중지
    hx_trigger = "every 1s" if job.status == CrawlStatus.RUNNING else ""
    
    # 다운로드 버튼
    download_button = ""
    if job.status == CrawlStatus.COMPLETED and job.result_file:
        download_button = f"""
        <div class="mt-4 flex gap-2">
            <a href="/downloads/{job.result_file}.json" 
               class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                📥 JSON 다운로드
            </a>
            <a href="/downloads/{job.result_file}.csv" 
               class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">
                📊 CSV 다운로드
            </a>
        </div>
        """
    
    return f"""
    <div id="job-{job.id}" 
         class="bg-white rounded-lg shadow p-6 border-l-4 border-{'green' if job.status == CrawlStatus.COMPLETED else 'blue'}-500"
         {'hx-get="/jobs/' + job.id + '/status" hx-trigger="' + hx_trigger + '" hx-swap="outerHTML"' if hx_trigger else ''}>
        <div class="flex justify-between items-start mb-4">
            <div>
                <h3 class="text-lg font-semibold">{job.name}</h3>
                <p class="text-sm text-gray-500">{job.url}</p>
            </div>
            <span class="px-3 py-1 {status_colors[job.status]} rounded-full text-sm">
                {job.status.value}
            </span>
        </div>
        
        <div class="w-full bg-gray-200 rounded-full h-2 mb-2">
            <div class="bg-{'green' if job.status == CrawlStatus.COMPLETED else 'blue'}-500 h-2 rounded-full transition-all duration-300" 
                 style="width: {job.progress}%"></div>
        </div>
        
        <div class="flex justify-between text-sm text-gray-600">
            <span>수집: {job.collected_items}/{job.total_items}</span>
            <span>에러: {job.error_count}</span>
            <span>{job.progress}%</span>
        </div>
        
        {download_button}
        
        <div class="mt-4">
            <button onclick="toggleLogs('{job.id}')" 
                    class="text-sm text-blue-600 hover:text-blue-800">
                로그 보기 ▼
            </button>
            <div id="logs-{job.id}" class="hidden mt-2 p-3 bg-gray-50 rounded text-xs font-mono max-h-40 overflow-y-auto">
                {'<br>'.join(job.logs[-10:])}
            </div>
        </div>
    </div>
    """


@app.delete("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """작업 취소"""
    job = app.state.jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status == CrawlStatus.RUNNING:
        crawler = app.state.crawlers.get(job_id)
        if crawler:
            crawler.cancel()
        job.status = CrawlStatus.CANCELLED
    
    return {"status": "cancelled"}


@app.get("/api/stats")
async def get_stats():
    """통계 API"""
    jobs = list(app.state.jobs.values())
    
    return {
        "total_jobs": len(jobs),
        "active_jobs": sum(1 for j in jobs if j.status == CrawlStatus.RUNNING),
        "completed_jobs": sum(1 for j in jobs if j.status == CrawlStatus.COMPLETED),
        "failed_jobs": sum(1 for j in jobs if j.status == CrawlStatus.FAILED),
        "total_collected": sum(j.collected_items for j in jobs),
        "total_errors": sum(j.error_count for j in jobs)
    }


@app.post("/quick-crawl", response_class=HTMLResponse)
async def quick_crawl(
    request: Request,
    url: str = Form(...)
):
    """빠른 크롤링 (자동 선택자 감지)"""
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 자동으로 주요 요소 감지
        auto_selectors = {}
        
        # 제목
        title = soup.find('h1') or soup.find('h2') or soup.find('title')
        if title:
            auto_selectors['title'] = title.name
        
        # 본문
        article = soup.find('article') or soup.find('main') or soup.find('div', class_='content')
        if article:
            auto_selectors['content'] = 'article' if soup.find('article') else 'main'
        
        # 이미지
        images = soup.find_all('img')[:5]
        if images:
            auto_selectors['images'] = 'img'
        
        # 링크
        links = soup.find_all('a', href=True)[:10]
        if links:
            auto_selectors['links'] = 'a[href]'
        
        # 자동 감지된 선택자로 작업 생성
        job = CrawlJob(
            id=str(uuid.uuid4()),
            name=f"Quick Crawl - {urlparse(url).netloc}",
            url=url,
            selectors=auto_selectors,
            created_at=datetime.now()
        )
        
        app.state.jobs[job.id] = job
        
        # 크롤링 시작
        crawler = AsyncCrawler(job.id, app)
        app.state.crawlers[job.id] = crawler
        asyncio.create_task(crawler.crawl(job))
        
        return f"""
        <div class="bg-green-50 border border-green-200 rounded p-4">
            <p class="text-green-800">✅ 자동 감지 완료!</p>
            <p class="text-sm text-gray-600 mt-2">감지된 선택자: {', '.join(auto_selectors.keys())}</p>
            <p class="text-sm text-gray-600">작업 ID: {job.id}</p>
        </div>
        """
        
    except Exception as e:
        return f"""
        <div class="bg-red-50 border border-red-200 rounded p-4">
            <p class="text-red-800">❌ 오류: {str(e)}</p>
        </div>
        """


# ==================== Templates 디렉토리 생성 ====================
if __name__ == "__main__":
    # templates 디렉토리가 없으면 생성
    Path("templates").mkdir(exist_ok=True)
    Path("static").mkdir(exist_ok=True)
    Path("downloads").mkdir(exist_ok=True)
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)