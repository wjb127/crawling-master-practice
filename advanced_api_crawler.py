#!/usr/bin/env python3
"""
고급 API 크롤러 - 네트워크 분석 및 역공학
실제 웹사이트의 API를 분석하여 직접 호출하는 고급 크롤링 기법
"""

import asyncio
import aiohttp
import requests
import json
import time
from datetime import datetime
import pandas as pd
from typing import List, Dict, Any
import hashlib
import hmac
from urllib.parse import urlencode, quote
from fake_useragent import UserAgent
from collections import deque
import random


class AdvancedAPICrawler:
    """고급 API 크롤러 - 여러 플랫폼의 내부 API 활용"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.session = None
        self.results = []
        self.rate_limiter = RateLimiter(max_requests=10, time_window=1)
        
    def get_headers(self, referer=None, custom_headers=None):
        """동적 헤더 생성"""
        headers = {
            'User-Agent': self.ua.random,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
        
        if referer:
            headers['Referer'] = referer
            
        if custom_headers:
            headers.update(custom_headers)
            
        return headers
    
    def analyze_instagram_api(self):
        """Instagram 공개 API 분석 및 데이터 수집"""
        print("\n" + "="*60)
        print("Instagram 해시태그 분석 (공개 데이터)")
        print("="*60)
        
        hashtag = "programming"
        url = f"https://www.instagram.com/explore/tags/{hashtag}/?__a=1&__d=dis"
        
        headers = self.get_headers(
            referer=f"https://www.instagram.com/explore/tags/{hashtag}/",
            custom_headers={
                'X-IG-App-ID': '936619743392459',
                'X-Requested-With': 'XMLHttpRequest',
            }
        )
        
        try:
            # Instagram은 로그인 없이는 제한적 접근만 가능
            print(f"해시태그 #{hashtag} 분석 시도...")
            print("(참고: Instagram은 공개 API가 제한적입니다)")
            
            # 대신 공개된 GraphQL 엔드포인트 활용 예제
            return self._mock_instagram_data(hashtag)
            
        except Exception as e:
            print(f"Instagram API 접근 실패: {e}")
            return []
    
    def _mock_instagram_data(self, hashtag):
        """Instagram 스타일 모의 데이터"""
        mock_data = {
            'hashtag': hashtag,
            'post_count': random.randint(100000, 1000000),
            'top_posts': [
                {
                    'id': f'post_{i}',
                    'likes': random.randint(1000, 50000),
                    'comments': random.randint(10, 1000),
                    'caption': f'Amazing {hashtag} content #{i}',
                    'timestamp': datetime.now().isoformat()
                }
                for i in range(5)
            ]
        }
        return mock_data
    
    def crawl_github_api(self):
        """GitHub API v3 활용 - 트렌딩 저장소 상세 정보"""
        print("\n" + "="*60)
        print("GitHub API v3 - 인기 저장소 상세 분석")
        print("="*60)
        
        # GitHub API는 인증 없이도 시간당 60회 요청 가능
        base_url = "https://api.github.com"
        
        # 1. Python 언어 인기 저장소 검색
        search_url = f"{base_url}/search/repositories"
        params = {
            'q': 'language:python stars:>1000',
            'sort': 'stars',
            'order': 'desc',
            'per_page': 10
        }
        
        headers = self.get_headers()
        headers['Accept'] = 'application/vnd.github.v3+json'
        
        try:
            response = requests.get(search_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            print(f"총 {data['total_count']:,}개의 Python 저장소 발견")
            print(f"상위 10개 분석 중...\n")
            
            repos_data = []
            for idx, repo in enumerate(data['items'], 1):
                repo_info = {
                    'rank': idx,
                    'name': repo['full_name'],
                    'stars': repo['stargazers_count'],
                    'forks': repo['forks_count'],
                    'language': repo['language'],
                    'description': repo['description'][:100] if repo['description'] else '',
                    'created_at': repo['created_at'],
                    'updated_at': repo['updated_at'],
                    'open_issues': repo['open_issues_count'],
                    'topics': repo.get('topics', [])[:5],
                    'url': repo['html_url']
                }
                
                repos_data.append(repo_info)
                print(f"[{idx}] {repo['full_name']} - ⭐ {repo['stargazers_count']:,}")
                
                # Rate limiting
                time.sleep(0.1)
            
            # CSV 저장
            df = pd.DataFrame(repos_data)
            df.to_csv('github_api_repos.csv', index=False, encoding='utf-8-sig')
            print(f"\n✓ 저장 완료: github_api_repos.csv")
            
            return repos_data
            
        except requests.exceptions.RequestException as e:
            print(f"GitHub API 오류: {e}")
            return []
    
    async def async_crawl_multiple_apis(self):
        """비동기로 여러 API 동시 크롤링"""
        print("\n" + "="*60)
        print("비동기 멀티 API 크롤링")
        print("="*60)
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            # 여러 공개 API 동시 호출
            apis = [
                ('JSONPlaceholder Posts', 'https://jsonplaceholder.typicode.com/posts'),
                ('JSONPlaceholder Users', 'https://jsonplaceholder.typicode.com/users'),
                ('Random User API', 'https://randomuser.me/api/?results=5'),
                ('CoinGecko Crypto', 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10'),
            ]
            
            for name, url in apis:
                task = self.fetch_api_async(session, name, url)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 결과 처리
            for name, result in results:
                if isinstance(result, Exception):
                    print(f"❌ {name}: 실패 - {result}")
                else:
                    if isinstance(result, list):
                        count = len(result)
                    elif isinstance(result, dict):
                        count = len(result.get('results', result))
                    else:
                        count = 1
                    print(f"✓ {name}: {count}개 데이터 수집")
            
            return results
    
    async def fetch_api_async(self, session, name, url):
        """비동기 API 호출"""
        try:
            headers = {'User-Agent': self.ua.random}
            async with session.get(url, headers=headers, timeout=10) as response:
                data = await response.json()
                return (name, data)
        except Exception as e:
            return (name, e)
    
    def crawl_hidden_api(self):
        """숨겨진 API 엔드포인트 발견 및 활용"""
        print("\n" + "="*60)
        print("Hidden API Discovery - Hacker News")
        print("="*60)
        
        # Hacker News의 공식 API (Firebase)
        base_url = "https://hacker-news.firebaseio.com/v0"
        
        try:
            # 1. Top Stories ID 가져오기
            top_stories_url = f"{base_url}/topstories.json"
            response = requests.get(top_stories_url)
            story_ids = response.json()[:20]  # 상위 20개만
            
            print(f"상위 {len(story_ids)}개 스토리 분석 중...")
            
            stories = []
            for idx, story_id in enumerate(story_ids, 1):
                # 2. 각 스토리 상세 정보 가져오기
                story_url = f"{base_url}/item/{story_id}.json"
                response = requests.get(story_url)
                story = response.json()
                
                if story:
                    story_info = {
                        'rank': idx,
                        'title': story.get('title', ''),
                        'score': story.get('score', 0),
                        'by': story.get('by', ''),
                        'time': datetime.fromtimestamp(story.get('time', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                        'descendants': story.get('descendants', 0),  # 댓글 수
                        'url': story.get('url', ''),
                        'type': story.get('type', '')
                    }
                    stories.append(story_info)
                    
                    print(f"[{idx}] {story_info['title'][:50]}... (점수: {story_info['score']})")
                
                # Rate limiting
                time.sleep(0.05)
            
            # 저장
            df = pd.DataFrame(stories)
            df.to_csv('hackernews_top_stories.csv', index=False, encoding='utf-8-sig')
            print(f"\n✓ 저장 완료: hackernews_top_stories.csv")
            
            return stories
            
        except Exception as e:
            print(f"Hacker News API 오류: {e}")
            return []
    
    def analyze_api_with_network_tools(self):
        """네트워크 도구로 API 분석하는 방법 설명"""
        print("\n" + "="*60)
        print("API 역공학 가이드")
        print("="*60)
        
        guide = """
        1. 브라우저 개발자 도구 활용:
           - F12 → Network 탭 → XHR/Fetch 필터
           - 페이지 동작 시 발생하는 API 호출 관찰
           - Request Headers, Payload, Response 분석
        
        2. 중요 체크 포인트:
           - Authorization 헤더 (Bearer token, API key)
           - X-로 시작하는 커스텀 헤더
           - Cookie 값 (세션 유지)
           - Request Body의 암호화/서명 여부
        
        3. API 패턴 분석:
           - RESTful: /api/v1/users/{id}
           - GraphQL: /graphql (POST with query)
           - WebSocket: wss:// 프로토콜
        
        4. Rate Limiting 우회:
           - User-Agent 로테이션
           - IP 프록시 로테이션
           - 요청 간격 랜덤화
           - 세션 재사용
        
        5. 실전 팁:
           - robots.txt 확인 (법적 문제 예방)
           - API 문서 먼저 찾기 (공식 제공 여부)
           - 점진적 접근 (소량 → 대량)
           - 에러 처리 철저히
        """
        
        print(guide)
        
        # 실제 API 분석 예제
        example = {
            'site': 'example.com',
            'api_endpoint': '/api/v2/search',
            'method': 'POST',
            'headers': {
                'X-API-Version': '2.0',
                'X-Client-ID': 'web-client',
                'Authorization': 'Bearer <token>'
            },
            'payload': {
                'query': 'search term',
                'page': 1,
                'limit': 20,
                'filters': {}
            }
        }
        
        print("\n실제 API 분석 예제:")
        print(json.dumps(example, indent=2, ensure_ascii=False))
        
        return example


class RateLimiter:
    """Rate Limiting 구현"""
    
    def __init__(self, max_requests=10, time_window=1):
        self.max_requests = max_requests
        self.time_window = time_window  # seconds
        self.requests = deque()
    
    async def acquire(self):
        """요청 허가 대기"""
        now = time.time()
        
        # 오래된 요청 제거
        while self.requests and self.requests[0] < now - self.time_window:
            self.requests.popleft()
        
        # 제한 확인
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
                return await self.acquire()
        
        # 요청 기록
        self.requests.append(now)


class APISignatureGenerator:
    """API 서명 생성기 (일부 API에서 필요)"""
    
    @staticmethod
    def generate_signature(secret_key: str, params: dict) -> str:
        """HMAC-SHA256 서명 생성"""
        # 파라미터 정렬 및 인코딩
        sorted_params = sorted(params.items())
        param_string = urlencode(sorted_params)
        
        # HMAC-SHA256 서명
        signature = hmac.new(
            secret_key.encode('utf-8'),
            param_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    @staticmethod
    def generate_nonce() -> str:
        """Nonce 생성 (일회용 값)"""
        return str(int(time.time() * 1000))


async def main_async():
    """비동기 메인 함수"""
    crawler = AdvancedAPICrawler()
    await crawler.async_crawl_multiple_apis()


def main():
    """메인 실행 함수"""
    print("="*60)
    print("고급 API 크롤러 - 실전 기법")
    print("="*60)
    
    crawler = AdvancedAPICrawler()
    
    # 1. GitHub API 크롤링
    github_data = crawler.crawl_github_api()
    
    # 2. Hacker News API 크롤링
    hn_data = crawler.crawl_hidden_api()
    
    # 3. Instagram 스타일 분석 (모의)
    insta_data = crawler.analyze_instagram_api()
    
    # 4. 비동기 멀티 API 크롤링
    print("\n비동기 크롤링 시작...")
    asyncio.run(main_async())
    
    # 5. API 역공학 가이드
    crawler.analyze_api_with_network_tools()
    
    print("\n" + "="*60)
    print("✅ 모든 API 크롤링 완료!")
    print("="*60)
    print("\n생성된 파일:")
    print("  - github_api_repos.csv (GitHub 인기 저장소)")
    print("  - hackernews_top_stories.csv (Hacker News Top Stories)")
    print("\n학습 포인트:")
    print("  1. 공개 API 활용법")
    print("  2. Hidden API 발견 및 활용")
    print("  3. 비동기 처리로 성능 최적화")
    print("  4. Rate Limiting 처리")
    print("  5. API 역공학 기법")


if __name__ == "__main__":
    main()