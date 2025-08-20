#!/usr/bin/env python3
"""
기본 웹 크롤러 예제
네이버 뉴스 IT/과학 섹션의 최신 기사 제목과 링크를 수집합니다.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import json
from fake_useragent import UserAgent

class NaverNewsCrawler:
    def __init__(self):
        self.ua = UserAgent()
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.base_url = "https://news.naver.com/section/105"  # IT/과학 섹션
        self.articles = []
        
    def fetch_page(self, url):
        """웹 페이지를 가져옵니다."""
        try:
            print(f"페이지 요청 중: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"페이지 요청 실패: {e}")
            return None
    
    def parse_articles(self, html):
        """HTML에서 기사 정보를 추출합니다."""
        soup = BeautifulSoup(html, 'lxml')
        
        # 네이버 뉴스 메인 기사 영역 찾기
        article_list = soup.select('div.section_latest_article ul li')
        
        for article in article_list:
            try:
                # 제목과 링크 추출
                title_elem = article.select_one('a.sa_text_title')
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                link = title_elem.get('href', '')
                
                # 언론사 정보
                press_elem = article.select_one('div.sa_text_press')
                press = press_elem.get_text(strip=True) if press_elem else 'Unknown'
                
                # 요약 내용
                summary_elem = article.select_one('div.sa_text_lede')
                summary = summary_elem.get_text(strip=True) if summary_elem else ''
                
                # 시간 정보
                time_elem = article.select_one('div.sa_text_datetime')
                publish_time = time_elem.get_text(strip=True) if time_elem else ''
                
                self.articles.append({
                    'title': title,
                    'link': link,
                    'press': press,
                    'summary': summary[:100] + '...' if len(summary) > 100 else summary,
                    'publish_time': publish_time,
                    'crawled_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
            except Exception as e:
                print(f"기사 파싱 중 오류: {e}")
                continue
    
    def crawl(self):
        """크롤링을 실행합니다."""
        print("네이버 뉴스 IT/과학 섹션 크롤링 시작...")
        
        html = self.fetch_page(self.base_url)
        if html:
            self.parse_articles(html)
            print(f"총 {len(self.articles)}개의 기사를 수집했습니다.")
        
        # 요청 간격 준수 (1초 대기)
        time.sleep(1)
        
        return self.articles
    
    def save_to_csv(self, filename='naver_news_it.csv'):
        """결과를 CSV 파일로 저장합니다."""
        if not self.articles:
            print("저장할 데이터가 없습니다.")
            return
        
        df = pd.DataFrame(self.articles)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"데이터를 {filename}에 저장했습니다.")
        
    def save_to_json(self, filename='naver_news_it.json'):
        """결과를 JSON 파일로 저장합니다."""
        if not self.articles:
            print("저장할 데이터가 없습니다.")
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.articles, f, ensure_ascii=False, indent=2)
        print(f"데이터를 {filename}에 저장했습니다.")
    
    def display_results(self):
        """수집한 결과를 출력합니다."""
        if not self.articles:
            print("출력할 데이터가 없습니다.")
            return
        
        print("\n" + "="*80)
        print("수집된 기사 목록")
        print("="*80)
        
        for idx, article in enumerate(self.articles[:10], 1):  # 상위 10개만 출력
            print(f"\n[{idx}] {article['title']}")
            print(f"    언론사: {article['press']}")
            print(f"    시간: {article['publish_time']}")
            print(f"    요약: {article['summary']}")
            print(f"    링크: {article['link']}")
            print("-" * 80)


def main():
    """메인 실행 함수"""
    crawler = NaverNewsCrawler()
    
    # 크롤링 실행
    articles = crawler.crawl()
    
    if articles:
        # 결과 출력
        crawler.display_results()
        
        # 파일로 저장
        crawler.save_to_csv()
        crawler.save_to_json()
        
        print(f"\n✅ 크롤링 완료!")
        print(f"   - 수집된 기사: {len(articles)}개")
        print(f"   - CSV 파일: naver_news_it.csv")
        print(f"   - JSON 파일: naver_news_it.json")
    else:
        print("❌ 크롤링 실패: 데이터를 수집하지 못했습니다.")


if __name__ == "__main__":
    main()