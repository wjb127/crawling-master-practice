#!/usr/bin/env python3
"""
간단한 동적 웹사이트 크롤러 - 무한 스크롤 예제
Selenium과 webdriver-manager를 사용하여 자동으로 드라이버 관리
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import json
import time
from datetime import datetime


class DynamicCrawler:
    def __init__(self, headless=True):
        self.driver = None
        self.headless = headless
        self.data = []
        
    def setup_driver(self):
        """Chrome WebDriver 자동 설정"""
        print("Chrome WebDriver 자동 설정 중...")
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless=new")
            
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        # WebDriver Manager를 사용하여 자동으로 드라이버 다운로드
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 자동화 감지 우회
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✓ WebDriver 설정 완료")
        return True
    
    def crawl_infinite_scroll_site(self):
        """무한 스크롤 사이트 예제 - 쿠팡 베스트"""
        url = "https://www.coupang.com/np/campaigns/82"
        
        print(f"\n크롤링 시작: 쿠팡 베스트 상품")
        print(f"URL: {url}")
        
        self.driver.get(url)
        time.sleep(3)  # 초기 로딩 대기
        
        # 스크롤 전 초기 상품 개수
        products = self.driver.find_elements(By.CSS_SELECTOR, "li.baby-product")
        print(f"초기 상품 개수: {len(products)}")
        
        # 3번 스크롤하여 더 많은 상품 로드
        for i in range(3):
            print(f"\n스크롤 {i+1}/3 진행 중...")
            
            # 현재 높이 저장
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # 스크롤 다운
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # 새로운 콘텐츠 로딩 확인
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                print("더 이상 로드할 콘텐츠가 없습니다.")
                break
            
            products = self.driver.find_elements(By.CSS_SELECTOR, "li.baby-product")
            print(f"현재 상품 개수: {len(products)}")
        
        # 상품 정보 추출
        print("\n상품 정보 추출 중...")
        products = self.driver.find_elements(By.CSS_SELECTOR, "li.baby-product")
        
        for idx, product in enumerate(products[:30], 1):  # 상위 30개만
            try:
                # 상품명
                try:
                    name = product.find_element(By.CSS_SELECTOR, "div.name").text
                except:
                    name = "상품명 없음"
                
                # 가격
                try:
                    price = product.find_element(By.CSS_SELECTOR, "strong.price-value").text
                except:
                    price = "가격 정보 없음"
                
                # 할인율
                try:
                    discount = product.find_element(By.CSS_SELECTOR, "span.discount-percentage").text
                except:
                    discount = ""
                
                # 평점
                try:
                    rating = product.find_element(By.CSS_SELECTOR, "em.rating").text
                except:
                    rating = ""
                
                # 리뷰 수
                try:
                    review_count = product.find_element(By.CSS_SELECTOR, "span.rating-total-count").text
                    review_count = review_count.strip("()")
                except:
                    review_count = ""
                
                self.data.append({
                    'rank': idx,
                    'name': name,
                    'price': price,
                    'discount': discount,
                    'rating': rating,
                    'review_count': review_count,
                    'crawled_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
                print(f"  [{idx}] {name[:40]}... - {price}")
                
            except Exception as e:
                print(f"  상품 {idx} 파싱 실패: {e}")
                continue
        
        return True
    
    def crawl_spa_site(self):
        """SPA(Single Page Application) 크롤링 예제"""
        url = "https://github.com/trending"
        
        print(f"\n크롤링 시작: GitHub Trending")
        print(f"URL: {url}")
        
        self.driver.get(url)
        
        # 동적 콘텐츠 로딩 대기
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article.Box-row"))
            )
            print("✓ 페이지 로딩 완료")
        except:
            print("❌ 페이지 로딩 실패")
            return False
        
        # 저장소 정보 추출
        repos = self.driver.find_elements(By.CSS_SELECTOR, "article.Box-row")
        print(f"총 {len(repos)}개의 트렌딩 저장소 발견\n")
        
        github_data = []
        for idx, repo in enumerate(repos[:10], 1):
            try:
                # 저장소 이름
                repo_name = repo.find_element(By.CSS_SELECTOR, "h2 a").text.strip()
                
                # 설명
                try:
                    description = repo.find_element(By.CSS_SELECTOR, "p.color-fg-muted").text
                except:
                    description = ""
                
                # 언어
                try:
                    language = repo.find_element(By.CSS_SELECTOR, "span[itemprop='programmingLanguage']").text
                except:
                    language = ""
                
                # 스타 수
                try:
                    stars = repo.find_element(By.CSS_SELECTOR, "a[href*='/stargazers'] svg").find_element(By.XPATH, "..").text.strip()
                except:
                    stars = ""
                
                github_data.append({
                    'rank': idx,
                    'repository': repo_name,
                    'description': description[:100],
                    'language': language,
                    'stars': stars
                })
                
                print(f"  [{idx}] {repo_name} - ⭐ {stars}")
                
            except Exception as e:
                continue
        
        # GitHub 데이터 저장
        if github_data:
            df = pd.DataFrame(github_data)
            df.to_csv('github_trending.csv', index=False, encoding='utf-8-sig')
            print(f"\n✓ GitHub Trending 저장: github_trending.csv")
        
        return True
    
    def save_results(self):
        """결과 저장"""
        if not self.data:
            print("저장할 데이터가 없습니다.")
            return
        
        # CSV 저장
        df = pd.DataFrame(self.data)
        df.to_csv('coupang_best.csv', index=False, encoding='utf-8-sig')
        print(f"\n✓ CSV 파일 저장: coupang_best.csv")
        
        # JSON 저장
        with open('coupang_best.json', 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print(f"✓ JSON 파일 저장: coupang_best.json")
        
        # 상위 5개 출력
        print("\n" + "="*80)
        print("쿠팡 베스트 상품 TOP 5")
        print("="*80)
        
        for item in self.data[:5]:
            print(f"\n[{item['rank']}위] {item['name']}")
            print(f"    가격: {item['price']}")
            if item['discount']:
                print(f"    할인: {item['discount']}")
            if item['rating']:
                print(f"    평점: {item['rating']} ({item['review_count']})")
    
    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()
            print("\n✓ WebDriver 종료")
    
    def run(self):
        """크롤링 실행"""
        try:
            if not self.setup_driver():
                return
            
            # 1. 무한 스크롤 사이트 크롤링 (쿠팡)
            if self.crawl_infinite_scroll_site():
                self.save_results()
            
            # 2. SPA 사이트 크롤링 (GitHub)
            self.crawl_spa_site()
            
        except Exception as e:
            print(f"크롤링 중 오류 발생: {e}")
        finally:
            self.close()


def main():
    """메인 실행 함수"""
    print("="*80)
    print("동적 웹사이트 크롤러 - Selenium 활용")
    print("="*80)
    
    # headless=False로 설정하면 브라우저가 실제로 열림
    crawler = DynamicCrawler(headless=True)
    crawler.run()
    
    print("\n✅ 모든 크롤링 완료!")
    print("생성된 파일:")
    print("  - coupang_best.csv/json (쿠팡 베스트 상품)")
    print("  - github_trending.csv (GitHub 트렌딩)")


if __name__ == "__main__":
    main()