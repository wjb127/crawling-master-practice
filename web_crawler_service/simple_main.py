#!/usr/bin/env python3
"""
심플한 FastAPI + HTMX 크롤링 서비스
DB 없이 메모리 저장 + 엑셀 다운로드
"""

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


# ==================== 설정 ====================
class CrawlStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class CrawlJob:
    def __init__(self, name: str, url: str, selectors: Dict[str, str]):
        self.id = str(uuid.uuid4())[:8]  # 짧은 ID
        self.name = name
        self.url = url
        self.selectors = selectors
        self.status = CrawlStatus.PENDING
        self.progress = 0
        self.total_items = 0
        self.collected_items = 0
        self.created_at = datetime.now()
        self.result_file = None
        self.data = []  # 수집된 데이터
        self.logs = []


# ==================== 앱 초기화 ====================
app = FastAPI(title="Simple Crawler")
templates = Jinja2Templates(directory="templates")

# 전역 저장소 (메모리)
jobs_store: Dict[str, CrawlJob] = {}

# 디렉토리 생성
Path("templates").mkdir(exist_ok=True)
Path("downloads").mkdir(exist_ok=True)
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")


# ==================== 크롤러 엔진 ====================
class SimpleCrawler:
    """심플한 비동기 크롤러"""
    
    def __init__(self, job: CrawlJob):
        self.job = job
        self.session = None
        
    async def crawl(self):
        """크롤링 실행"""
        try:
            self.job.status = CrawlStatus.RUNNING
            self.log(f"🚀 크롤링 시작: {self.job.url}")
            
            async with aiohttp.ClientSession() as self.session:
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
                            # 여러 개면 리스트로, 하나면 텍스트로
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
                
                # 추가 페이지 찾기 (옵션)
                links = self.find_similar_links(soup, self.job.url)
                self.job.total_items = len(links) + 1
                
                # 최대 10개 추가 페이지만 크롤링
                for idx, link in enumerate(links[:10], 1):
                    self.job.progress = int((idx / min(len(links) + 1, 11)) * 100)
                    self.log(f"📄 페이지 {idx}/{ min(len(links), 10)} 크롤링 중...")
                    
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
                    
                    await asyncio.sleep(0.5)  # Rate limiting
                
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
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            async with self.session.get(url, headers=headers, timeout=10, ssl=False) as response:
                if response.status == 200:
                    return await response.text()
        except Exception as e:
            self.log(f"페이지 요청 실패: {str(e)}")
        return None
    
    def find_similar_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """비슷한 패턴의 링크 찾기"""
        links = set()
        base_domain = urlparse(base_url).netloc
        
        for a in soup.find_all('a', href=True)[:50]:  # 최대 50개만 확인
            href = a['href']
            full_url = urljoin(base_url, href)
            
            # 같은 도메인이고, 특정 패턴이 있으면 추가
            if urlparse(full_url).netloc == base_domain:
                # 뉴스, 상품, 게시글 등의 패턴
                if any(pattern in full_url for pattern in ['/article/', '/product/', '/post/', '/item/', '/news/']):
                    links.add(full_url)
        
        return list(links)[:20]  # 최대 20개
    
    def save_to_excel(self):
        """엑셀 파일로 저장 (스타일 포함)"""
        try:
            df = pd.DataFrame(self.job.data)
            
            # 파일명 생성
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.job.name.replace(' ', '_')}_{timestamp}"
            filepath = f"downloads/{filename}.xlsx"
            
            # 엑셀 Writer 생성
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='크롤링 결과', index=False)
                
                # 워크시트 가져오기
                worksheet = writer.sheets['크롤링 결과']
                
                # 헤더 스타일
                header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
                header_font = Font(color='FFFFFF', bold=True)
                
                for cell in worksheet[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal='center')
                
                # 컬럼 너비 자동 조정
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            self.job.result_file = filename
            self.log(f"📊 엑셀 파일 생성: {filename}.xlsx")
            
        except Exception as e:
            self.log(f"엑셀 저장 실패: {str(e)}")
    
    def log(self, message: str):
        """로그 추가"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.job.logs.append(f"[{timestamp}] {message}")
        print(f"[{self.job.id}] {message}")


# ==================== API 엔드포인트 ====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """메인 페이지"""
    jobs = list(jobs_store.values())
    jobs.sort(key=lambda x: x.created_at, reverse=True)
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "jobs": jobs[:20],  # 최근 20개만 표시
            "active_count": sum(1 for j in jobs if j.status == CrawlStatus.RUNNING),
            "completed_count": sum(1 for j in jobs if j.status == CrawlStatus.COMPLETED),
            "total_collected": sum(len(j.data) for j in jobs)
        }
    )


@app.post("/jobs/create", response_class=HTMLResponse)
async def create_job(
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
            parts = line.split(':', 1)
            if len(parts) == 2:
                field = parts[0].strip()
                selector = parts[1].strip()
                if field and selector:
                    selector_dict[field] = selector
    
    # 기본 선택자 추가 (비어있으면)
    if not selector_dict:
        selector_dict = {
            'title': 'h1, h2, title',
            'content': 'p, article, .content',
            'links': 'a[href]'
        }
    
    # Job 생성
    job = CrawlJob(name=name, url=url, selectors=selector_dict)
    jobs_store[job.id] = job
    
    # 백그라운드에서 크롤링 시작
    crawler = SimpleCrawler(job)
    background_tasks.add_task(crawler.crawl)
    
    # HTMX용 작업 카드 반환
    return f"""
    <div id="job-{job.id}" 
         class="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500 animate-pulse-border"
         hx-get="/jobs/{job.id}/status"
         hx-trigger="every 1s"
         hx-swap="outerHTML">
        <div class="flex justify-between items-start mb-4">
            <div class="flex-1 min-w-0">
                <h3 class="text-lg font-semibold truncate">{job.name}</h3>
                <p class="text-sm text-gray-500 truncate">{job.url}</p>
            </div>
            <span class="ml-2 px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm">
                준비 중
            </span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
            <div class="bg-blue-500 h-2 rounded-full" style="width: 0%"></div>
        </div>
        <div class="mt-2 text-sm text-gray-600">
            크롤링 준비 중...
        </div>
    </div>
    """


@app.get("/jobs/{job_id}/status", response_class=HTMLResponse)
async def get_job_status(job_id: str):
    """작업 상태 조회"""
    job = jobs_store.get(job_id)
    if not job:
        return "<div>작업을 찾을 수 없습니다</div>"
    
    # 상태별 색상
    colors = {
        CrawlStatus.PENDING: "yellow",
        CrawlStatus.RUNNING: "blue",
        CrawlStatus.COMPLETED: "green",
        CrawlStatus.FAILED: "red"
    }
    
    color = colors[job.status]
    
    # 진행 중이 아니면 polling 중지
    hx_attrs = 'hx-get="/jobs/' + job_id + '/status" hx-trigger="every 1s" hx-swap="outerHTML"' if job.status == CrawlStatus.RUNNING else ''
    
    # 다운로드 버튼
    download_button = ""
    if job.status == CrawlStatus.COMPLETED and job.result_file:
        download_button = f"""
        <div class="mt-4">
            <a href="/downloads/{job.result_file}.xlsx" 
               class="inline-flex items-center px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                엑셀 다운로드 ({len(job.data)}개 항목)
            </a>
        </div>
        """
    
    # 로그 표시 (최근 5개)
    recent_logs = '<br>'.join(job.logs[-5:]) if job.logs else '로그 없음'
    
    return f"""
    <div id="job-{job.id}" 
         class="bg-white rounded-lg shadow p-6 border-l-4 border-{color}-500"
         {hx_attrs}>
        <div class="flex justify-between items-start mb-4">
            <div class="flex-1 min-w-0">
                <h3 class="text-lg font-semibold truncate">{job.name}</h3>
                <p class="text-sm text-gray-500 truncate">{job.url}</p>
            </div>
            <span class="ml-2 px-3 py-1 bg-{color}-100 text-{color}-800 rounded-full text-sm">
                {job.status.value}
            </span>
        </div>
        
        <div class="w-full bg-gray-200 rounded-full h-2 mb-2">
            <div class="bg-{color}-500 h-2 rounded-full transition-all duration-300" 
                 style="width: {job.progress}%"></div>
        </div>
        
        <div class="flex justify-between text-sm text-gray-600">
            <span>수집: {job.collected_items}/{min(job.total_items, 11)}</span>
            <span>{job.progress}%</span>
        </div>
        
        {download_button}
        
        <details class="mt-4">
            <summary class="cursor-pointer text-sm text-blue-600 hover:text-blue-800">
                로그 보기
            </summary>
            <div class="mt-2 p-3 bg-gray-50 rounded text-xs font-mono text-gray-600">
                {recent_logs}
            </div>
        </details>
    </div>
    """


@app.post("/quick-crawl", response_class=HTMLResponse)
async def quick_crawl(
    background_tasks: BackgroundTasks,
    url: str = Form(...)
):
    """빠른 크롤링 (자동 선택자)"""
    
    # 자동 선택자 설정
    auto_selectors = {
        'title': 'h1, h2, h3, title',
        'description': 'meta[name="description"], p:first-of-type',
        'content': 'article, main, .content, .post-content, .entry-content',
        'images': 'img[src]',
        'links': 'a[href]'
    }
    
    # Job 생성
    domain = urlparse(url).netloc
    job = CrawlJob(
        name=f"Quick - {domain}",
        url=url,
        selectors=auto_selectors
    )
    jobs_store[job.id] = job
    
    # 크롤링 시작
    crawler = SimpleCrawler(job)
    background_tasks.add_task(crawler.crawl)
    
    return f"""
    <div class="bg-green-50 border border-green-200 rounded-lg p-4">
        <div class="flex items-center">
            <svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <p class="text-green-800 font-semibold">자동 크롤링 시작!</p>
        </div>
        <p class="text-sm text-gray-600 mt-2">작업 ID: {job.id}</p>
        <p class="text-sm text-gray-500">자동 감지된 필드: {', '.join(auto_selectors.keys())}</p>
    </div>
    <script>
        setTimeout(() => location.reload(), 2000);
    </script>
    """


# ==================== 실행 ====================
if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*50)
    print("🕷️  크롤링 마스터 서버 시작!")
    print("="*50)
    print("📍 주소: http://localhost:8000")
    print("📊 엑셀 파일은 downloads 폴더에 저장됩니다")
    print("="*50 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)