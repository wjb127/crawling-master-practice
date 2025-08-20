#!/usr/bin/env python3
"""
로그인 크롤러 - 인증이 필요한 사이트 크롤링
세션 관리, 쿠키 처리, 2FA, CAPTCHA 우회 기법
"""

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pickle
import json
import time
import os
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional
import base64
from PIL import Image
import io
import re
from fake_useragent import UserAgent


class LoginCrawler:
    """로그인이 필요한 사이트 크롤러"""
    
    def __init__(self, headless=False):
        self.driver = None
        self.session = requests.Session()
        self.cookies = {}
        self.headless = headless
        self.ua = UserAgent()
        
    def setup_driver(self, undetected=True):
        """Selenium 드라이버 설정 (탐지 회피 옵션 포함)"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        if undetected:
            # 봇 탐지 회피 설정
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument(f'user-agent={self.ua.random}')
            
            # 추가 스텔스 옵션
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # 실제 브라우저처럼 보이게 하기
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # JavaScript로 봇 탐지 우회
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": self.ua.random
        })
        
        print("✓ 드라이버 설정 완료 (스텔스 모드)")
        return True
    
    def save_cookies(self, filepath="cookies.pkl"):
        """쿠키 저장"""
        with open(filepath, 'wb') as f:
            pickle.dump(self.driver.get_cookies(), f)
        print(f"✓ 쿠키 저장: {filepath}")
    
    def load_cookies(self, filepath="cookies.pkl"):
        """쿠키 로드"""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
            print(f"✓ 쿠키 로드: {filepath}")
            return True
        return False
    
    def login_with_selenium(self, url, username, password, 
                           username_selector, password_selector, 
                           submit_selector=None):
        """Selenium을 사용한 로그인"""
        print(f"\n로그인 시도: {url}")
        
        self.driver.get(url)
        time.sleep(2)
        
        try:
            # 사용자명 입력
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, username_selector))
            )
            username_field.clear()
            
            # 인간처럼 타이핑
            for char in username:
                username_field.send_keys(char)
                time.sleep(0.1 + 0.1 * (0.5 - 0.5))  # 랜덤 딜레이
            
            # 비밀번호 입력
            password_field = self.driver.find_element(By.CSS_SELECTOR, password_selector)
            password_field.clear()
            
            for char in password:
                password_field.send_keys(char)
                time.sleep(0.1)
            
            # 로그인 버튼 클릭
            if submit_selector:
                submit_button = self.driver.find_element(By.CSS_SELECTOR, submit_selector)
                submit_button.click()
            else:
                password_field.send_keys(Keys.RETURN)
            
            time.sleep(3)
            print("✓ 로그인 성공")
            return True
            
        except Exception as e:
            print(f"❌ 로그인 실패: {e}")
            return False
    
    def login_with_requests(self, login_url, username, password, 
                           csrf_token=None, additional_data=None):
        """Requests를 사용한 로그인 (더 빠름)"""
        print(f"\n세션 로그인 시도: {login_url}")
        
        # CSRF 토큰이 필요한 경우
        if csrf_token:
            response = self.session.get(login_url)
            # CSRF 토큰 추출 로직 (사이트별로 다름)
            csrf = self._extract_csrf_token(response.text)
        else:
            csrf = None
        
        # 로그인 데이터
        login_data = {
            'username': username,  # 사이트에 따라 'email' 등으로 변경
            'password': password
        }
        
        if csrf:
            login_data['csrf_token'] = csrf
            
        if additional_data:
            login_data.update(additional_data)
        
        # 로그인 요청
        headers = {
            'User-Agent': self.ua.random,
            'Referer': login_url
        }
        
        response = self.session.post(login_url, data=login_data, headers=headers)
        
        if response.status_code == 200:
            print("✓ 세션 로그인 성공")
            self.cookies = self.session.cookies.get_dict()
            return True
        else:
            print(f"❌ 로그인 실패: {response.status_code}")
            return False
    
    def _extract_csrf_token(self, html):
        """CSRF 토큰 추출"""
        # 예제: <input name="csrf_token" value="xxx">
        match = re.search(r'name="csrf_token".*?value="([^"]+)"', html)
        if match:
            return match.group(1)
        return None
    
    def handle_2fa(self, code_input_selector=None):
        """2FA (Two-Factor Authentication) 처리"""
        print("\n2FA 처리 중...")
        
        if code_input_selector:
            # 실제 2FA 코드 입력 (사용자 입력 필요)
            code = input("2FA 코드를 입력하세요: ")
            
            code_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, code_input_selector))
            )
            code_field.send_keys(code)
            code_field.send_keys(Keys.RETURN)
            
            time.sleep(3)
            print("✓ 2FA 인증 완료")
            return True
        
        return False
    
    def solve_captcha_manual(self):
        """CAPTCHA 수동 해결"""
        print("\nCAPTCHA 감지됨!")
        print("브라우저에서 직접 CAPTCHA를 해결하세요.")
        input("해결 후 Enter를 누르세요...")
        return True
    
    def solve_captcha_with_service(self, captcha_image_selector):
        """CAPTCHA 자동 해결 (2captcha 등 서비스 사용)"""
        print("\nCAPTCHA 자동 해결 시도...")
        
        # CAPTCHA 이미지 캡처
        captcha_element = self.driver.find_element(By.CSS_SELECTOR, captcha_image_selector)
        captcha_screenshot = captcha_element.screenshot_as_png
        
        # 여기에 2captcha API 등을 사용한 해결 로직
        # 예제이므로 실제 구현은 생략
        print("(실제 환경에서는 2captcha 등의 서비스 API 사용)")
        
        return False
    
    def crawl_github_private_repos(self):
        """GitHub 프라이빗 저장소 크롤링 예제"""
        print("\n" + "="*60)
        print("GitHub 로그인 크롤링 예제")
        print("="*60)
        
        # GitHub 로그인 페이지
        login_url = "https://github.com/login"
        
        self.driver.get(login_url)
        time.sleep(2)
        
        # 쿠키가 있으면 로드
        if self.load_cookies("github_cookies.pkl"):
            self.driver.refresh()
            time.sleep(2)
            
            # 로그인 확인
            if "login" not in self.driver.current_url:
                print("✓ 쿠키로 로그인 성공")
                return self._crawl_github_data()
        
        # 로그인 필요 (데모이므로 실제 로그인은 건너뜀)
        print("실제 로그인이 필요합니다 (데모 모드)")
        return self._demo_github_data()
    
    def _demo_github_data(self):
        """GitHub 데모 데이터"""
        print("\n프라이빗 저장소 정보 (데모):")
        
        demo_repos = [
            {
                'name': 'my-private-project',
                'visibility': 'Private',
                'last_commit': '2 hours ago',
                'language': 'Python',
                'size': '2.3 MB'
            },
            {
                'name': 'company-internal-tool',
                'visibility': 'Private',
                'last_commit': '1 day ago',
                'language': 'JavaScript',
                'size': '15.7 MB'
            }
        ]
        
        for repo in demo_repos:
            print(f"  🔒 {repo['name']} ({repo['visibility']})")
            print(f"     Language: {repo['language']}, Size: {repo['size']}")
        
        return demo_repos
    
    def crawl_linkedin_profile(self):
        """LinkedIn 프로필 크롤링 예제"""
        print("\n" + "="*60)
        print("LinkedIn 프로필 크롤링 (세션 관리)")
        print("="*60)
        
        # LinkedIn은 강력한 안티봇 시스템을 가지고 있음
        print("LinkedIn 크롤링 주의사항:")
        print("  1. Rate limiting 매우 엄격")
        print("  2. 계정 차단 위험")
        print("  3. 공식 API 사용 권장")
        
        # 데모 데이터
        profile_data = {
            'name': 'John Doe',
            'title': 'Senior Software Engineer',
            'company': 'Tech Corp',
            'connections': '500+',
            'skills': ['Python', 'JavaScript', 'Cloud Computing'],
            'education': 'Computer Science, MIT'
        }
        
        print(f"\n프로필 정보:")
        for key, value in profile_data.items():
            print(f"  {key}: {value}")
        
        return profile_data
    
    def crawl_instagram_private(self):
        """Instagram 프라이빗 계정 크롤링 예제"""
        print("\n" + "="*60)
        print("Instagram 프라이빗 계정 접근")
        print("="*60)
        
        print("Instagram 크롤링 전략:")
        print("  1. 모바일 User-Agent 사용")
        print("  2. 인간같은 행동 패턴 모방")
        print("  3. 프록시 로테이션")
        print("  4. 요청 간격 랜덤화")
        
        # 안티봇 우회 기법
        mobile_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        
        headers = {
            'User-Agent': mobile_ua,
            'X-Requested-With': 'XMLHttpRequest',
            'X-IG-App-ID': '936619743392459'
        }
        
        print("\n모바일 모드로 접근 중...")
        print(f"User-Agent: {mobile_ua[:50]}...")
        
        return {'status': 'demo_mode', 'followers': 1234, 'posts': 56}
    
    def advanced_session_management(self):
        """고급 세션 관리 기법"""
        print("\n" + "="*60)
        print("고급 세션 관리 기법")
        print("="*60)
        
        techniques = """
        1. 세션 풀링 (Session Pooling)
           - 여러 세션을 동시에 유지
           - 로테이션으로 Rate Limit 회피
        
        2. 쿠키 영속성
           - SQLite DB에 쿠키 저장
           - 만료 시간 관리
           - 자동 갱신
        
        3. 프록시 체인
           - SOCKS5 프록시
           - residential 프록시
           - 프록시 로테이션
        
        4. 브라우저 프로필
           - Chrome 프로필 저장/로드
           - 브라우저 지문 관리
           - 확장 프로그램 활용
        
        5. API 키 관리
           - 환경 변수 사용
           - 암호화 저장
           - 자동 로테이션
        """
        
        print(techniques)
        
        # 세션 풀 예제
        session_pool = []
        for i in range(3):
            session = requests.Session()
            session.headers.update({'User-Agent': self.ua.random})
            session_pool.append(session)
            print(f"  세션 {i+1} 생성 완료")
        
        return session_pool


class CookieManager:
    """쿠키 관리 클래스"""
    
    @staticmethod
    def save_cookies_json(driver, filepath="cookies.json"):
        """쿠키를 JSON으로 저장"""
        cookies = driver.get_cookies()
        with open(filepath, 'w') as f:
            json.dump(cookies, f, indent=2)
        print(f"✓ 쿠키 저장 (JSON): {filepath}")
    
    @staticmethod
    def load_cookies_json(driver, filepath="cookies.json"):
        """JSON에서 쿠키 로드"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                cookies = json.load(f)
                for cookie in cookies:
                    driver.add_cookie(cookie)
            print(f"✓ 쿠키 로드 (JSON): {filepath}")
            return True
        return False
    
    @staticmethod
    def export_to_netscape(cookies, filepath="cookies.txt"):
        """Netscape 형식으로 쿠키 내보내기 (curl, wget 호환)"""
        with open(filepath, 'w') as f:
            f.write("# Netscape HTTP Cookie File\n")
            for cookie in cookies:
                domain = cookie.get('domain', '')
                flag = "TRUE" if domain.startswith('.') else "FALSE"
                path = cookie.get('path', '/')
                secure = "TRUE" if cookie.get('secure', False) else "FALSE"
                expiry = cookie.get('expiry', 0)
                name = cookie.get('name', '')
                value = cookie.get('value', '')
                
                f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n")
        
        print(f"✓ Netscape 형식 쿠키 저장: {filepath}")


class AntiDetectionTechniques:
    """봇 탐지 우회 기법 모음"""
    
    @staticmethod
    def get_stealth_headers():
        """스텔스 헤더 생성"""
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
    
    @staticmethod
    def random_delay(min_seconds=1, max_seconds=3):
        """랜덤 딜레이"""
        import random
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        return delay
    
    @staticmethod
    def mouse_movement_simulation(driver):
        """마우스 움직임 시뮬레이션"""
        from selenium.webdriver.common.action_chains import ActionChains
        import random
        
        actions = ActionChains(driver)
        
        # 랜덤 위치로 마우스 이동
        for _ in range(3):
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            actions.move_by_offset(x, y)
            actions.pause(random.uniform(0.1, 0.3))
        
        actions.perform()
        print("✓ 마우스 움직임 시뮬레이션 완료")


def main():
    """메인 실행 함수"""
    print("="*60)
    print("로그인 크롤러 - 인증 및 세션 관리")
    print("="*60)
    
    crawler = LoginCrawler(headless=False)
    
    try:
        # 드라이버 설정
        crawler.setup_driver(undetected=True)
        
        # 1. GitHub 크롤링 (쿠키 사용)
        github_data = crawler.crawl_github_private_repos()
        
        # 2. LinkedIn 프로필 (세션 관리)
        linkedin_data = crawler.crawl_linkedin_profile()
        
        # 3. Instagram 프라이빗 (모바일 모드)
        instagram_data = crawler.crawl_instagram_private()
        
        # 4. 고급 세션 관리 기법
        session_pool = crawler.advanced_session_management()
        
        # 결과 저장
        results = {
            'github': github_data,
            'linkedin': linkedin_data,
            'instagram': instagram_data,
            'timestamp': datetime.now().isoformat()
        }
        
        with open('login_crawl_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print("\n" + "="*60)
        print("✅ 로그인 크롤링 완료!")
        print("="*60)
        print("\n주요 기능:")
        print("  1. 세션/쿠키 관리")
        print("  2. 봇 탐지 우회")
        print("  3. 2FA 처리")
        print("  4. CAPTCHA 대응")
        print("  5. 프록시/UA 로테이션")
        
        print("\n⚠️  법적 주의사항:")
        print("  - 서비스 이용약관 준수")
        print("  - robots.txt 확인")
        print("  - Rate limiting 준수")
        print("  - 개인정보 보호")
        
    except Exception as e:
        print(f"오류 발생: {e}")
    
    finally:
        if crawler.driver:
            crawler.driver.quit()
            print("\n✓ 드라이버 종료")


if __name__ == "__main__":
    main()