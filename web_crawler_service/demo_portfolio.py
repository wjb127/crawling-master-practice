"""
인터랙티브 크롤링 포트폴리오 데모
원클릭으로 모든 크롤링 예제를 실행할 수 있는 FastAPI 웹 애플리케이션
"""

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json
import os
import subprocess
from typing import Dict, List, Any
import uuid

app = FastAPI(title="크롤링 포트폴리오 데모")

# 템플릿 설정
templates = Jinja2Templates(directory="templates")

# 다운로드 디렉토리 생성
os.makedirs("downloads", exist_ok=True)
os.makedirs("demo_results", exist_ok=True)

# 데모 상태 저장
demo_status: Dict[str, Any] = {}

class DemoRunner:
    """데모 실행 클래스"""
    
    @staticmethod
    async def run_basic_crawler():
        """기본 BeautifulSoup 크롤러 실행"""
        try:
            # Naver IT 뉴스 크롤링
            url = "https://news.naver.com/section/105"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as response:
                    html = await response.text()
            
            soup = BeautifulSoup(html, 'html.parser')
            articles = []
            
            # 뉴스 기사 추출
            for item in soup.select('.sa_text')[:10]:
                title = item.select_one('.sa_text_title')
                desc = item.select_one('.sa_text_lede')
                if title:
                    articles.append({
                        'title': title.get_text(strip=True),
                        'description': desc.get_text(strip=True) if desc else '',
                        'timestamp': datetime.now().isoformat()
                    })
            
            # 결과 저장
            df = pd.DataFrame(articles)
            filename = f"demo_basic_crawler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(f"demo_results/{filename}", index=False)
            
            return {
                "status": "success",
                "message": f"✅ 기본 크롤러 실행 완료! {len(articles)}개 기사 수집",
                "data": articles[:3],  # 미리보기용
                "file": filename
            }
        except Exception as e:
            return {"status": "error", "message": f"❌ 오류 발생: {str(e)}"}
    
    @staticmethod
    async def run_api_crawler():
        """API 크롤러 실행 (GitHub API)"""
        try:
            # GitHub Trending API
            url = "https://api.github.com/search/repositories"
            params = {
                "q": "language:python stars:>1000",
                "sort": "stars",
                "order": "desc",
                "per_page": 10
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    data = await response.json()
            
            repos = []
            for repo in data.get('items', []):
                repos.append({
                    'name': repo['full_name'],
                    'stars': repo['stargazers_count'],
                    'language': repo.get('language', 'Unknown'),
                    'description': repo.get('description', ''),
                    'url': repo['html_url']
                })
            
            # 결과 저장
            df = pd.DataFrame(repos)
            filename = f"demo_api_crawler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(f"demo_results/{filename}", index=False)
            
            return {
                "status": "success",
                "message": f"✅ API 크롤러 실행 완료! Top {len(repos)} Python 레포지토리 수집",
                "data": repos[:3],
                "file": filename
            }
        except Exception as e:
            return {"status": "error", "message": f"❌ 오류 발생: {str(e)}"}
    
    @staticmethod
    async def run_async_crawler():
        """비동기 멀티 사이트 크롤러"""
        try:
            sites = [
                {"name": "Hacker News", "url": "https://news.ycombinator.com"},
                {"name": "Reddit Programming", "url": "https://www.reddit.com/r/programming.json"},
                {"name": "Dev.to", "url": "https://dev.to/api/articles?per_page=10"}
            ]
            
            results = []
            
            async def fetch_site(site):
                try:
                    async with aiohttp.ClientSession() as session:
                        headers = {"User-Agent": "Mozilla/5.0"}
                        async with session.get(site["url"], headers=headers, timeout=10) as response:
                            if site["name"] == "Reddit Programming":
                                data = await response.json()
                                return {
                                    "site": site["name"],
                                    "status": "success",
                                    "items": len(data.get("data", {}).get("children", [])),
                                    "sample": data.get("data", {}).get("children", [])[0] if data.get("data", {}).get("children") else None
                                }
                            elif site["name"] == "Dev.to":
                                data = await response.json()
                                return {
                                    "site": site["name"],
                                    "status": "success",
                                    "items": len(data),
                                    "sample": data[0] if data else None
                                }
                            else:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                return {
                                    "site": site["name"],
                                    "status": "success",
                                    "items": len(soup.select('.titleline')),
                                    "html_length": len(html)
                                }
                except Exception as e:
                    return {
                        "site": site["name"],
                        "status": "error",
                        "error": str(e)
                    }
            
            # 비동기로 모든 사이트 동시 크롤링
            tasks = [fetch_site(site) for site in sites]
            results = await asyncio.gather(*tasks)
            
            # 결과 저장
            df = pd.DataFrame(results)
            filename = f"demo_async_crawler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(f"demo_results/{filename}", index=False)
            
            return {
                "status": "success",
                "message": f"✅ 비동기 크롤러 실행 완료! {len(results)}개 사이트 동시 크롤링",
                "data": results,
                "file": filename
            }
        except Exception as e:
            return {"status": "error", "message": f"❌ 오류 발생: {str(e)}"}
    
    @staticmethod
    async def run_smart_selector():
        """스마트 CSS 선택자 자동 감지"""
        try:
            # 테스트 HTML
            test_html = """
            <html>
                <head><title>테스트 페이지</title></head>
                <body>
                    <article>
                        <h1 class="main-title">메인 제목입니다</h1>
                        <div class="author">홍길동</div>
                        <time datetime="2024-01-01">2024년 1월 1일</time>
                        <div class="content">
                            <p>첫 번째 문단입니다.</p>
                            <p>두 번째 문단입니다.</p>
                        </div>
                        <div class="tags">
                            <span class="tag">Python</span>
                            <span class="tag">크롤링</span>
                            <span class="tag">자동화</span>
                        </div>
                    </article>
                </body>
            </html>
            """
            
            soup = BeautifulSoup(test_html, 'html.parser')
            
            # 자동 선택자 감지
            selectors = {}
            
            # 제목 감지
            for selector in ['h1', 'h2', '.main-title', '.title', 'article h1']:
                if soup.select_one(selector):
                    selectors['title'] = selector
                    break
            
            # 작성자 감지
            for selector in ['.author', '.writer', '.by', 'span.author']:
                if soup.select_one(selector):
                    selectors['author'] = selector
                    break
            
            # 날짜 감지
            for selector in ['time', '.date', '.timestamp', 'span.date']:
                if soup.select_one(selector):
                    selectors['date'] = selector
                    break
            
            # 내용 감지
            for selector in ['.content p', 'article p', '.body', 'div.content']:
                if soup.select(selector):
                    selectors['content'] = selector
                    break
            
            # 태그 감지
            for selector in ['.tag', '.tags span', '.category']:
                if soup.select(selector):
                    selectors['tags'] = selector
                    break
            
            # 감지된 선택자로 데이터 추출
            extracted_data = {}
            for key, selector in selectors.items():
                elements = soup.select(selector)
                if elements:
                    if len(elements) == 1:
                        extracted_data[key] = elements[0].get_text(strip=True)
                    else:
                        extracted_data[key] = [el.get_text(strip=True) for el in elements]
            
            return {
                "status": "success",
                "message": "✅ 스마트 선택자 자동 감지 완료!",
                "selectors": selectors,
                "extracted_data": extracted_data
            }
        except Exception as e:
            return {"status": "error", "message": f"❌ 오류 발생: {str(e)}"}
    
    @staticmethod
    async def run_data_cleaning():
        """데이터 정제 및 변환 데모"""
        try:
            # 샘플 더러운 데이터
            dirty_data = [
                {"title": "  제목1  \n\n", "price": "₩50,000원", "date": "2024-01-01"},
                {"title": "제목2!!!!", "price": "$100 USD", "date": "01/02/2024"},
                {"title": None, "price": "가격 미정", "date": "2024년 1월 3일"},
                {"title": "제목4<script>alert('xss')</script>", "price": "150000", "date": "2024-01-04T10:00:00"}
            ]
            
            # 데이터 정제
            cleaned_data = []
            for item in dirty_data:
                cleaned = {}
                
                # 제목 정제
                if item.get('title'):
                    title = item['title']
                    title = title.strip()  # 공백 제거
                    title = title.replace('!', '')  # 특수문자 제거
                    # XSS 방지
                    soup = BeautifulSoup(title, 'html.parser')
                    title = soup.get_text()
                    cleaned['title'] = title
                else:
                    cleaned['title'] = "제목 없음"
                
                # 가격 정제 (숫자만 추출)
                price = item.get('price', '0')
                import re
                price_nums = re.findall(r'\d+', price.replace(',', ''))
                cleaned['price'] = int(price_nums[0]) if price_nums else 0
                
                # 날짜 정제 (표준 형식으로)
                date = item.get('date', '')
                # 여러 날짜 형식 처리
                try:
                    if 'T' in date:
                        date = date.split('T')[0]
                    elif '/' in date:
                        parts = date.split('/')
                        date = f"2024-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
                    elif '년' in date:
                        date = "2024-01-03"  # 간단한 처리
                    cleaned['date'] = date
                except:
                    cleaned['date'] = datetime.now().strftime('%Y-%m-%d')
                
                cleaned_data.append(cleaned)
            
            # 결과 저장
            df_before = pd.DataFrame(dirty_data)
            df_after = pd.DataFrame(cleaned_data)
            
            filename = f"demo_data_cleaning_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            with pd.ExcelWriter(f"demo_results/{filename}") as writer:
                df_before.to_excel(writer, sheet_name='Before', index=False)
                df_after.to_excel(writer, sheet_name='After', index=False)
            
            return {
                "status": "success",
                "message": "✅ 데이터 정제 완료!",
                "before": dirty_data,
                "after": cleaned_data,
                "file": filename
            }
        except Exception as e:
            return {"status": "error", "message": f"❌ 오류 발생: {str(e)}"}

# 라우트 정의
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """메인 포트폴리오 페이지"""
    return templates.TemplateResponse("demo_portfolio.html", {"request": request})

@app.post("/demo/run/{demo_type}")
async def run_demo(demo_type: str, background_tasks: BackgroundTasks):
    """데모 실행"""
    demo_id = str(uuid.uuid4())[:8]
    
    # 데모 타입별 실행
    runner = DemoRunner()
    
    if demo_type == "basic":
        result = await runner.run_basic_crawler()
    elif demo_type == "api":
        result = await runner.run_api_crawler()
    elif demo_type == "async":
        result = await runner.run_async_crawler()
    elif demo_type == "smart":
        result = await runner.run_smart_selector()
    elif demo_type == "cleaning":
        result = await runner.run_data_cleaning()
    else:
        result = {"status": "error", "message": "Unknown demo type"}
    
    demo_status[demo_id] = result
    return JSONResponse({"demo_id": demo_id, **result})

@app.get("/demo/status/{demo_id}")
async def get_demo_status(demo_id: str):
    """데모 상태 확인"""
    return JSONResponse(demo_status.get(demo_id, {"status": "not_found"}))

@app.get("/demo/download/{filename}")
async def download_result(filename: str):
    """결과 파일 다운로드"""
    file_path = f"demo_results/{filename}"
    if os.path.exists(file_path):
        return FileResponse(
            file_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=filename
        )
    return JSONResponse({"error": "File not found"}, status_code=404)

@app.get("/test/run")
async def run_tests():
    """TDD 테스트 실행"""
    try:
        # pytest 실행
        result = subprocess.run(
            ["python", "-m", "pytest", "test_crawlers.py", "-v", "--tb=short", "--json-report", "--json-report-file=test_report.json"],
            capture_output=True,
            text=True,
            cwd="/Users/seungbeenwi/Project/crawling-practice2/web_crawler_service"
        )
        
        # 테스트 결과 파싱
        if os.path.exists("test_report.json"):
            with open("test_report.json", "r") as f:
                report = json.load(f)
                return JSONResponse({
                    "status": "success",
                    "passed": report.get("summary", {}).get("passed", 0),
                    "failed": report.get("summary", {}).get("failed", 0),
                    "total": report.get("summary", {}).get("total", 0),
                    "output": result.stdout
                })
        
        return JSONResponse({
            "status": "success",
            "output": result.stdout,
            "errors": result.stderr
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)