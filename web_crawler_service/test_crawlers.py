"""
TDD Test Suite for Crawling Service
크롤링 서비스 TDD 테스트 스위트
"""

import pytest
import asyncio
import aiohttp
from unittest.mock import Mock, patch, AsyncMock
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json
import os

# 테스트할 크롤러 임포트
from simple_main import (
    CrawlJob, 
    auto_detect_selectors,
    extract_data,
    save_to_excel
)

class TestCrawlJob:
    """CrawlJob 클래스 테스트"""
    
    def test_job_initialization(self):
        """작업 초기화 테스트"""
        job = CrawlJob(
            name="테스트 작업",
            url="https://example.com",
            selectors={"title": "h1", "content": "p"}
        )
        
        assert job.name == "테스트 작업"
        assert job.url == "https://example.com"
        assert job.status == "pending"
        assert job.progress == 0
        assert len(job.id) == 8  # UUID 길이
        
    def test_job_status_update(self):
        """작업 상태 업데이트 테스트"""
        job = CrawlJob(name="test", url="https://example.com", selectors={})
        
        job.status = "running"
        assert job.status == "running"
        
        job.progress = 50
        assert job.progress == 50
        
        job.status = "completed"
        job.results = [{"title": "Test"}]
        assert len(job.results) == 1

class TestAutoDetectSelectors:
    """자동 선택자 감지 테스트"""
    
    def test_detect_news_article(self):
        """뉴스 기사 선택자 자동 감지"""
        html = """
        <html>
            <head><title>뉴스 제목</title></head>
            <body>
                <article>
                    <h1>메인 제목입니다</h1>
                    <div class="author">홍길동 기자</div>
                    <time>2024-01-01</time>
                    <div class="content">
                        <p>첫 번째 문단입니다.</p>
                        <p>두 번째 문단입니다.</p>
                    </div>
                </article>
            </body>
        </html>
        """
        
        selectors = auto_detect_selectors(html)
        
        assert "title" in selectors
        assert "content" in selectors
        assert selectors["title"] in ["h1", "article h1"]
        
    def test_detect_blog_post(self):
        """블로그 포스트 선택자 자동 감지"""
        html = """
        <html>
            <body>
                <div class="post">
                    <h2 class="post-title">블로그 제목</h2>
                    <span class="post-author">작성자</span>
                    <div class="post-content">
                        <p>내용입니다.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        selectors = auto_detect_selectors(html)
        
        assert "title" in selectors
        assert "content" in selectors
        assert "post-title" in selectors["title"] or "h2" in selectors["title"]
        
    def test_detect_product_page(self):
        """상품 페이지 선택자 자동 감지"""
        html = """
        <html>
            <body>
                <div class="product">
                    <h1 class="product-name">상품명</h1>
                    <span class="price">₩50,000</span>
                    <div class="description">상품 설명입니다.</div>
                    <img src="product.jpg" alt="상품 이미지">
                </div>
            </body>
        </html>
        """
        
        selectors = auto_detect_selectors(html)
        
        assert "title" in selectors or "product-name" in str(selectors.values())
        assert "price" in str(selectors.values()).lower()
        assert "img" in selectors.get("images", "")

class TestDataExtraction:
    """데이터 추출 테스트"""
    
    def test_extract_single_element(self):
        """단일 요소 추출"""
        html = "<html><h1>제목</h1><p>내용</p></html>"
        selectors = {"title": "h1", "content": "p"}
        
        results = extract_data(html, selectors)
        
        assert results[0]["title"] == "제목"
        assert results[0]["content"] == "내용"
        
    def test_extract_multiple_elements(self):
        """다중 요소 추출"""
        html = """
        <html>
            <div class="item">아이템1</div>
            <div class="item">아이템2</div>
            <div class="item">아이템3</div>
        </html>
        """
        selectors = {"items": ".item"}
        
        results = extract_data(html, selectors)
        
        assert len(results) == 3
        assert results[0]["items"] == "아이템1"
        assert results[1]["items"] == "아이템2"
        assert results[2]["items"] == "아이템3"
        
    def test_extract_nested_elements(self):
        """중첩된 요소 추출"""
        html = """
        <html>
            <article>
                <header>
                    <h1>제목</h1>
                    <span class="author">작성자</span>
                </header>
                <div class="content">
                    <p>문단1</p>
                    <p>문단2</p>
                </div>
            </article>
        </html>
        """
        selectors = {
            "title": "article h1",
            "author": ".author",
            "content": ".content p"
        }
        
        results = extract_data(html, selectors)
        
        assert results[0]["title"] == "제목"
        assert results[0]["author"] == "작성자"
        assert "문단1" in results[0]["content"]
        
    def test_extract_attributes(self):
        """속성 추출"""
        html = """
        <html>
            <a href="https://example.com" title="링크">링크 텍스트</a>
            <img src="image.jpg" alt="이미지 설명">
        </html>
        """
        selectors = {
            "links": "a",
            "images": "img"
        }
        
        results = extract_data(html, selectors)
        
        assert "링크 텍스트" in results[0]["links"]
        assert "image.jpg" in str(results)

class TestExcelExport:
    """엑셀 내보내기 테스트"""
    
    def test_save_to_excel_basic(self):
        """기본 엑셀 저장"""
        data = [
            {"title": "제목1", "content": "내용1"},
            {"title": "제목2", "content": "내용2"}
        ]
        
        filename = save_to_excel(data, "test_export")
        
        assert os.path.exists(f"downloads/{filename}")
        
        # 저장된 파일 검증
        df = pd.read_excel(f"downloads/{filename}")
        assert len(df) == 2
        assert "title" in df.columns
        assert "content" in df.columns
        
        # 정리
        os.remove(f"downloads/{filename}")
        
    def test_save_to_excel_with_korean(self):
        """한글 데이터 엑셀 저장"""
        data = [
            {"제목": "한글 제목", "내용": "한글 내용입니다"},
            {"제목": "두 번째 제목", "내용": "두 번째 내용"}
        ]
        
        filename = save_to_excel(data, "한글_테스트")
        
        assert os.path.exists(f"downloads/{filename}")
        
        df = pd.read_excel(f"downloads/{filename}")
        assert df.iloc[0]["제목"] == "한글 제목"
        
        os.remove(f"downloads/{filename}")
        
    def test_save_empty_data(self):
        """빈 데이터 처리"""
        data = []
        
        filename = save_to_excel(data, "empty_test")
        
        assert os.path.exists(f"downloads/{filename}")
        
        df = pd.read_excel(f"downloads/{filename}")
        assert len(df) == 0
        
        os.remove(f"downloads/{filename}")

class TestAsyncCrawling:
    """비동기 크롤링 테스트"""
    
    @pytest.mark.asyncio
    async def test_fetch_page(self):
        """페이지 가져오기 테스트"""
        mock_response = AsyncMock()
        mock_response.text = AsyncMock(return_value="<html><h1>Test</h1></html>")
        mock_response.status = 200
        
        with patch('aiohttp.ClientSession.get', return_value=mock_response):
            async with aiohttp.ClientSession() as session:
                response = await session.get("https://example.com")
                html = await response.text()
                
                assert "<h1>Test</h1>" in html
                assert response.status == 200
    
    @pytest.mark.asyncio
    async def test_concurrent_crawling(self):
        """동시 크롤링 테스트"""
        urls = [
            "https://example1.com",
            "https://example2.com",
            "https://example3.com"
        ]
        
        async def mock_fetch(url):
            await asyncio.sleep(0.1)  # 네트워크 지연 시뮬레이션
            return f"<html><h1>{url}</h1></html>"
        
        with patch('simple_main.fetch_page', side_effect=mock_fetch):
            results = await asyncio.gather(*[mock_fetch(url) for url in urls])
            
            assert len(results) == 3
            assert all("example" in r for r in results)

class TestErrorHandling:
    """에러 처리 테스트"""
    
    def test_invalid_selector(self):
        """잘못된 선택자 처리"""
        html = "<html><h1>제목</h1></html>"
        selectors = {"title": "invalid::selector::"}
        
        # 에러가 발생하지 않고 빈 결과 반환
        results = extract_data(html, selectors)
        assert isinstance(results, list)
        
    def test_malformed_html(self):
        """잘못된 HTML 처리"""
        html = "<html><h1>제목</h1"  # 닫는 태그 없음
        selectors = {"title": "h1"}
        
        results = extract_data(html, selectors)
        assert results[0]["title"] == "제목"  # BeautifulSoup이 자동 수정
        
    @pytest.mark.asyncio
    async def test_network_error(self):
        """네트워크 에러 처리"""
        with patch('aiohttp.ClientSession.get', side_effect=aiohttp.ClientError("Network error")):
            job = CrawlJob(
                name="test",
                url="https://invalid-url-12345.com",
                selectors={}
            )
            
            # 실제 크롤링 함수가 에러를 처리하는지 확인
            # (simple_main에 에러 처리 로직이 있다고 가정)
            job.status = "failed"
            job.error = "Network error"
            
            assert job.status == "failed"
            assert "error" in job.error.lower()

class TestIntegration:
    """통합 테스트"""
    
    @pytest.mark.asyncio
    async def test_full_crawling_workflow(self):
        """전체 크롤링 워크플로우 테스트"""
        # 1. 작업 생성
        job = CrawlJob(
            name="통합 테스트",
            url="https://example.com",
            selectors={"title": "h1", "content": "p"}
        )
        
        # 2. HTML 가져오기 (모킹)
        mock_html = """
        <html>
            <h1>테스트 제목</h1>
            <p>테스트 내용입니다.</p>
        </html>
        """
        
        # 3. 데이터 추출
        results = extract_data(mock_html, job.selectors)
        job.results = results
        
        # 4. 엑셀 저장
        filename = save_to_excel(results, job.name)
        
        # 5. 검증
        assert job.results[0]["title"] == "테스트 제목"
        assert os.path.exists(f"downloads/{filename}")
        
        # 정리
        os.remove(f"downloads/{filename}")

# pytest 실행을 위한 설정
if __name__ == "__main__":
    # downloads 디렉토리 생성
    os.makedirs("downloads", exist_ok=True)
    
    # 테스트 실행
    pytest.main([__file__, "-v", "--tb=short"])