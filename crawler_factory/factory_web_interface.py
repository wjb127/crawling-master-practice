"""
크롤러 팩토리 웹 인터페이스
고객 요구사항을 입력받아 자동으로 크롤러를 생성하는 웹 서비스
"""

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json
import shutil
import tempfile
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
import zipfile

# Factory system import
from factory_system import CrawlerFactory

app = FastAPI(title="크롤러 팩토리", version="1.0.0")

# Templates setup
templates_dir = Path(__file__).parent / "templates"
templates_dir.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))

# Static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Storage for generation jobs
generation_jobs: Dict[str, Dict[str, Any]] = {}

# Factory instance
factory = CrawlerFactory()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """메인 페이지 - 크롤러 생성 폼"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/generate")
async def generate_crawler(
    request: Request,
    background_tasks: BackgroundTasks
):
    """크롤러 생성 요청 처리"""
    form_data = await request.json()
    
    # Generate unique job ID
    job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Parse customer requirements
    customer_request = {
        "project_name": form_data.get("project_name", "CustomCrawler"),
        "company_name": form_data.get("company_name", "Customer Company"),
        "target_sites": form_data.get("target_sites", []),
        "data_fields": form_data.get("data_fields", []),
        "output_format": form_data.get("output_format", "excel"),
        "crawling_method": form_data.get("crawling_method", "static"),
        "login_required": form_data.get("login_required", False),
        "schedule_required": form_data.get("schedule_required", False),
        "proxy_support": form_data.get("proxy_support", False),
        "multi_threading": form_data.get("multi_threading", True),
        "error_retry": form_data.get("error_retry", True),
        "custom_features": form_data.get("custom_features", [])
    }
    
    # Store job info
    generation_jobs[job_id] = {
        "status": "processing",
        "progress": 0,
        "created_at": datetime.now().isoformat(),
        "request": customer_request,
        "output_path": None,
        "error": None
    }
    
    # Start background generation
    background_tasks.add_task(
        generate_crawler_background,
        job_id,
        customer_request
    )
    
    return JSONResponse({
        "job_id": job_id,
        "status": "started",
        "message": "크롤러 생성이 시작되었습니다."
    })

async def generate_crawler_background(job_id: str, customer_request: Dict[str, Any]):
    """백그라운드에서 크롤러 생성"""
    try:
        # Update progress
        generation_jobs[job_id]["progress"] = 10
        generation_jobs[job_id]["status"] = "generating"
        
        # Create output directory
        output_dir = Path(tempfile.mkdtemp()) / customer_request["project_name"]
        
        # Generate crawler using factory
        generation_jobs[job_id]["progress"] = 30
        project_path = factory.create_custom_crawler(customer_request)
        
        # Create installer if path exists
        generation_jobs[job_id]["progress"] = 60
        if project_path and Path(project_path).exists():
            # Build executable
            generation_jobs[job_id]["progress"] = 70
            factory.build_executable(project_path)
            
            # Create installer
            generation_jobs[job_id]["progress"] = 85
            installer_path = factory.create_installer(project_path)
            
            # Create zip package
            generation_jobs[job_id]["progress"] = 95
            zip_path = Path(project_path).parent / f"{customer_request['project_name']}_package.zip"
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all project files
                for root, dirs, files in os.walk(project_path):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(Path(project_path).parent)
                        zipf.write(file_path, arcname)
                
                # Add installer if exists
                if installer_path and Path(installer_path).exists():
                    zipf.write(installer_path, Path(installer_path).name)
            
            generation_jobs[job_id]["output_path"] = str(zip_path)
            generation_jobs[job_id]["installer_path"] = str(installer_path) if installer_path else None
        
        # Complete
        generation_jobs[job_id]["progress"] = 100
        generation_jobs[job_id]["status"] = "completed"
        
    except Exception as e:
        generation_jobs[job_id]["status"] = "failed"
        generation_jobs[job_id]["error"] = str(e)

@app.get("/api/status/{job_id}")
async def get_job_status(job_id: str):
    """생성 작업 상태 조회"""
    if job_id not in generation_jobs:
        return JSONResponse(
            {"error": "Job not found"},
            status_code=404
        )
    
    job = generation_jobs[job_id]
    return JSONResponse({
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "created_at": job["created_at"],
        "error": job["error"]
    })

@app.get("/api/download/{job_id}")
async def download_crawler(job_id: str):
    """생성된 크롤러 다운로드"""
    if job_id not in generation_jobs:
        return JSONResponse(
            {"error": "Job not found"},
            status_code=404
        )
    
    job = generation_jobs[job_id]
    if job["status"] != "completed":
        return JSONResponse(
            {"error": "Job not completed"},
            status_code=400
        )
    
    if not job["output_path"] or not Path(job["output_path"]).exists():
        return JSONResponse(
            {"error": "Output file not found"},
            status_code=404
        )
    
    return FileResponse(
        job["output_path"],
        media_type="application/zip",
        filename=f"{job['request']['project_name']}_package.zip"
    )

@app.get("/api/presets")
async def get_presets():
    """사전 정의된 프리셋 목록"""
    presets = [
        {
            "id": "ecommerce",
            "name": "이커머스 상품 크롤러",
            "description": "쇼핑몰 상품 정보 수집",
            "data_fields": ["상품명", "가격", "할인율", "리뷰수", "평점", "이미지URL"],
            "features": ["가격 추적", "재고 확인", "리뷰 분석"]
        },
        {
            "id": "news",
            "name": "뉴스 기사 크롤러",
            "description": "뉴스 사이트 기사 수집",
            "data_fields": ["제목", "본문", "작성자", "날짜", "카테고리", "조회수"],
            "features": ["키워드 필터링", "중복 제거", "요약 생성"]
        },
        {
            "id": "social",
            "name": "소셜 미디어 크롤러",
            "description": "SNS 게시물 수집",
            "data_fields": ["작성자", "내용", "좋아요수", "댓글수", "해시태그", "작성일"],
            "features": ["인플루언서 추적", "트렌드 분석", "감성 분석"]
        },
        {
            "id": "realestate",
            "name": "부동산 매물 크롤러",
            "description": "부동산 사이트 매물 정보",
            "data_fields": ["매물유형", "가격", "면적", "위치", "층수", "연락처"],
            "features": ["가격 변동 추적", "지역별 분류", "알림 기능"]
        },
        {
            "id": "job",
            "name": "채용공고 크롤러",
            "description": "구인구직 사이트 채용정보",
            "data_fields": ["회사명", "직무", "연봉", "경력", "마감일", "복지"],
            "features": ["키워드 매칭", "연봉 통계", "기업 정보"]
        }
    ]
    return JSONResponse(presets)

@app.get("/api/examples")
async def get_examples():
    """예제 요구사항"""
    examples = [
        {
            "title": "네이버 쇼핑 베스트100",
            "description": "네이버 쇼핑 카테고리별 베스트 상품 100개 수집",
            "requirements": {
                "target_sites": ["https://shopping.naver.com"],
                "data_fields": ["순위", "상품명", "가격", "할인율", "리뷰수"],
                "output_format": "excel",
                "schedule_required": True
            }
        },
        {
            "title": "부동산 시세 모니터링",
            "description": "특정 지역 아파트 매매/전세 시세 일일 수집",
            "requirements": {
                "target_sites": ["직방", "다방", "네이버부동산"],
                "data_fields": ["단지명", "면적", "매매가", "전세가", "거래일"],
                "output_format": "database",
                "schedule_required": True
            }
        },
        {
            "title": "경쟁사 가격 모니터링",
            "description": "경쟁사 제품 가격 변동 실시간 추적",
            "requirements": {
                "target_sites": ["쿠팡", "11번가", "G마켓"],
                "data_fields": ["상품코드", "상품명", "판매가", "할인가", "재고"],
                "output_format": "api",
                "schedule_required": True,
                "custom_features": ["가격 변동 알림", "재고 소진 알림"]
            }
        }
    ]
    return JSONResponse(examples)

if __name__ == "__main__":
    import uvicorn
    
    print("🏭 크롤러 팩토리 웹 인터페이스 시작...")
    print("📍 http://localhost:8001 에서 접속 가능합니다")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=True
    )