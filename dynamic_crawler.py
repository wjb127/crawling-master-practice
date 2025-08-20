#!/usr/bin/env python3
"""
동적 웹사이트 크롤러 - YouTube 인기 동영상
Selenium을 사용하여 JavaScript로 렌더링되는 콘텐츠를 크롤링합니다.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import json
import time
from datetime import datetime
import re


class YouTubeTrendingCrawler:
    def __init__(self, headless=True):
        """
        YouTube 트렌딩 크롤러 초기화
        
        Args:
            headless: 브라우저를 화면에 표시하지 않을지 여부
        """
        self.videos = []
        self.driver = None
        self.headless = headless
        
    def setup_driver(self):
        """Selenium WebDriver 설정"""
        print("Chrome WebDriver 설정 중...")
        
        # Chrome 옵션 설정
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")  # 백그라운드 실행
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        # 불필요한 로그 제거
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_argument("--log-level=3")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✓ WebDriver 설정 완료")
        except Exception as e:
            print(f"WebDriver 설정 실패: {e}")
            print("Chrome 드라이버가 설치되어 있는지 확인하세요.")
            return False
        
        return True
    
    def parse_view_count(self, view_text):
        """조회수 텍스트를 숫자로 변환"""
        if not view_text:
            return 0
        
        # "조회수 1.2만회" -> 12000
        # "조회수 523만회" -> 5230000
        # "조회수 1.5천회" -> 1500
        
        view_text = view_text.replace("조회수", "").replace("회", "").strip()
        
        if "만" in view_text:
            number = float(view_text.replace("만", "").replace(",", ""))
            return int(number * 10000)
        elif "천" in view_text:
            number = float(view_text.replace("천", "").replace(",", ""))
            return int(number * 1000)
        elif "억" in view_text:
            number = float(view_text.replace("억", "").replace(",", ""))
            return int(number * 100000000)
        else:
            try:
                return int(view_text.replace(",", ""))
            except:
                return 0
    
    def scroll_page(self, scroll_count=3):
        """페이지 스크롤하여 더 많은 콘텐츠 로드"""
        print(f"페이지 스크롤 중... (총 {scroll_count}회)")
        
        for i in range(scroll_count):
            # 페이지 끝까지 스크롤
            self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)  # 콘텐츠 로딩 대기
            print(f"  스크롤 {i+1}/{scroll_count} 완료")
    
    def crawl_youtube_trending(self):
        """YouTube 인기 동영상 크롤링"""
        url = "https://www.youtube.com/feed/trending"
        
        print(f"\n크롤링 시작: {url}")
        self.driver.get(url)
        
        # 페이지 로딩 대기
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "ytd-video-renderer"))
            )
            print("✓ 페이지 로딩 완료")
        except TimeoutException:
            print("❌ 페이지 로딩 타임아웃")
            return False
        
        # 스크롤하여 더 많은 동영상 로드
        self.scroll_page(scroll_count=3)
        
        # 동영상 정보 추출
        video_elements = self.driver.find_elements(By.TAG_NAME, "ytd-video-renderer")
        print(f"\n총 {len(video_elements)}개의 동영상 발견")
        
        for idx, video in enumerate(video_elements, 1):
            try:
                # 제목
                title_element = video.find_element(By.ID, "video-title")
                title = title_element.text
                video_url = title_element.get_attribute("href")
                
                # 채널명
                try:
                    channel = video.find_element(By.CSS_SELECTOR, "#channel-name #text").text
                except:
                    channel = "Unknown"
                
                # 조회수 및 업로드 시간
                metadata_elements = video.find_elements(By.CSS_SELECTOR, "#metadata-line span")
                views = ""
                upload_time = ""
                
                if len(metadata_elements) >= 2:
                    views = metadata_elements[0].text
                    upload_time = metadata_elements[1].text
                
                # 썸네일
                try:
                    thumbnail = video.find_element(By.CSS_SELECTOR, "img#img").get_attribute("src")
                except:
                    thumbnail = ""
                
                # 동영상 길이
                try:
                    duration = video.find_element(By.CSS_SELECTOR, "span#text.ytd-thumbnail-overlay-time-status-renderer").text
                except:
                    duration = ""
                
                # 조회수 파싱
                view_count = self.parse_view_count(views)
                
                self.videos.append({
                    'rank': idx,
                    'title': title,
                    'channel': channel,
                    'views': views,
                    'view_count': view_count,
                    'upload_time': upload_time,
                    'duration': duration,
                    'url': video_url,
                    'thumbnail': thumbnail,
                    'crawled_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
                print(f"  [{idx}] {title[:50]}... - {channel}")
                
            except Exception as e:
                print(f"  ❌ 동영상 {idx} 파싱 실패: {e}")
                continue
        
        return True
    
    def crawl_google_search(self, query="Python programming"):
        """Google 검색 결과 크롤링 (동적 로딩 예제)"""
        url = f"https://www.google.com/search?q={query}"
        
        print(f"\n🔍 Google 검색 크롤링: '{query}'")
        self.driver.get(url)
        
        # 검색 결과 로딩 대기
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.g"))
            )
        except TimeoutException:
            print("검색 결과 로딩 실패")
            return []
        
        search_results = []
        result_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.g")[:10]
        
        for idx, result in enumerate(result_elements, 1):
            try:
                # 제목과 링크
                title_elem = result.find_element(By.CSS_SELECTOR, "h3")
                title = title_elem.text
                
                link_elem = result.find_element(By.CSS_SELECTOR, "a")
                link = link_elem.get_attribute("href")
                
                # 설명
                try:
                    desc_elem = result.find_element(By.CSS_SELECTOR, "span.aCOpRe, div.VwiC3b")
                    description = desc_elem.text
                except:
                    description = ""
                
                search_results.append({
                    'rank': idx,
                    'title': title,
                    'link': link,
                    'description': description[:200]
                })
                
                print(f"  [{idx}] {title[:50]}...")
                
            except Exception as e:
                continue
        
        return search_results
    
    def save_results(self):
        """결과 저장"""
        if not self.videos:
            print("저장할 데이터가 없습니다.")
            return
        
        # CSV 저장
        df = pd.DataFrame(self.videos)
        df.to_csv('youtube_trending.csv', index=False, encoding='utf-8-sig')
        print(f"✓ CSV 파일 저장: youtube_trending.csv")
        
        # JSON 저장
        with open('youtube_trending.json', 'w', encoding='utf-8') as f:
            json.dump(self.videos, f, ensure_ascii=False, indent=2)
        print(f"✓ JSON 파일 저장: youtube_trending.json")
        
        # 상위 10개 출력
        print("\n" + "="*80)
        print("YouTube 인기 동영상 TOP 10")
        print("="*80)
        
        for video in self.videos[:10]:
            print(f"\n[{video['rank']}위] {video['title']}")
            print(f"    채널: {video['channel']}")
            print(f"    조회수: {video['views']} ({video['view_count']:,})")
            print(f"    업로드: {video['upload_time']}")
            print(f"    길이: {video['duration']}")
            print(f"    URL: {video['url']}")
    
    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()
            print("✓ WebDriver 종료")
    
    def run(self):
        """크롤링 실행"""
        try:
            # 드라이버 설정
            if not self.setup_driver():
                return
            
            # YouTube 크롤링
            if self.crawl_youtube_trending():
                self.save_results()
            
            # Google 검색 예제 (선택적)
            # search_results = self.crawl_google_search("Python web scraping")
            # print(f"\nGoogle 검색 결과: {len(search_results)}개")
            
        except Exception as e:
            print(f"크롤링 중 오류 발생: {e}")
        finally:
            self.close()


def main():
    """메인 실행 함수"""
    print("="*80)
    print("동적 웹사이트 크롤러 - YouTube 인기 동영상")
    print("="*80)
    
    # headless=False로 설정하면 브라우저가 실제로 열림
    crawler = YouTubeTrendingCrawler(headless=True)
    crawler.run()
    
    print("\n✅ 크롤링 완료!")


if __name__ == "__main__":
    main()