#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
크롤링 마스터 v1.0 - Windows Desktop Application
실시간 웹 크롤링 및 CSV 내보내기 툴
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import json
import os
import sys
from datetime import datetime
from urllib.parse import urlparse, urljoin
import webbrowser
import time

# 앱 정보
APP_NAME = "크롤링 마스터"
APP_VERSION = "1.0.0"
APP_AUTHOR = "크몽 프리랜서"

class CrawlerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("900x700")
        
        # 아이콘 설정 (있다면)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # 스타일 설정
        self.setup_styles()
        
        # 변수 초기화
        self.is_crawling = False
        self.crawl_thread = None
        self.results = []
        
        # UI 생성
        self.create_widgets()
        
        # 기본 폴더 생성
        os.makedirs("results", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
    def setup_styles(self):
        """UI 스타일 설정"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 색상 테마
        self.colors = {
            'primary': '#2196F3',
            'success': '#4CAF50',
            'danger': '#F44336',
            'warning': '#FF9800',
            'dark': '#212121',
            'light': '#F5F5F5'
        }
        
        style.configure('Title.TLabel', font=('맑은 고딕', 16, 'bold'))
        style.configure('Heading.TLabel', font=('맑은 고딕', 11, 'bold'))
        style.configure('Success.TButton', font=('맑은 고딕', 10, 'bold'))
        
    def create_widgets(self):
        """UI 위젯 생성"""
        
        # 메인 컨테이너
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 헤더
        self.create_header(main_frame)
        
        # 입력 섹션
        self.create_input_section(main_frame)
        
        # 선택자 섹션
        self.create_selector_section(main_frame)
        
        # 컨트롤 버튼
        self.create_control_buttons(main_frame)
        
        # 진행 상황
        self.create_progress_section(main_frame)
        
        # 로그 섹션
        self.create_log_section(main_frame)
        
        # 결과 미리보기
        self.create_result_preview(main_frame)
        
        # 상태바
        self.create_status_bar()
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
    def create_header(self, parent):
        """헤더 생성"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        title = ttk.Label(header_frame, text=f"🕷️ {APP_NAME}", style='Title.TLabel')
        title.pack(side=tk.LEFT)
        
        version = ttk.Label(header_frame, text=f"v{APP_VERSION}", font=('맑은 고딕', 9))
        version.pack(side=tk.LEFT, padx=(10, 0))
        
    def create_input_section(self, parent):
        """URL 입력 섹션"""
        input_frame = ttk.LabelFrame(parent, text="크롤링 설정", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # URL 입력
        ttk.Label(input_frame, text="URL:").grid(row=0, column=0, sticky=tk.W)
        self.url_var = tk.StringVar(value="https://news.naver.com/section/105")
        self.url_entry = ttk.Entry(input_frame, textvariable=self.url_var, width=60)
        self.url_entry.grid(row=0, column=1, padx=(5, 10), sticky=(tk.W, tk.E))
        
        # URL 검증 버튼
        self.check_btn = ttk.Button(input_frame, text="연결 테스트", command=self.test_connection)
        self.check_btn.grid(row=0, column=2)
        
        # 페이지 수 설정
        ttk.Label(input_frame, text="수집 페이지 수:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.pages_var = tk.IntVar(value=1)
        pages_spin = ttk.Spinbox(input_frame, from_=1, to=100, textvariable=self.pages_var, width=10)
        pages_spin.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=(10, 0))
        
        # 지연 시간
        ttk.Label(input_frame, text="지연 시간(초):").grid(row=1, column=1, sticky=tk.E, pady=(10, 0))
        self.delay_var = tk.DoubleVar(value=0.5)
        delay_spin = ttk.Spinbox(input_frame, from_=0.1, to=5.0, increment=0.1, 
                                 textvariable=self.delay_var, width=10)
        delay_spin.grid(row=1, column=2, pady=(10, 0))
        
        input_frame.columnconfigure(1, weight=1)
        
    def create_selector_section(self, parent):
        """CSS 선택자 섹션"""
        selector_frame = ttk.LabelFrame(parent, text="데이터 추출 설정", padding="10")
        selector_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 프리셋 버튼들
        preset_frame = ttk.Frame(selector_frame)
        preset_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(preset_frame, text="빠른 설정:").pack(side=tk.LEFT, padx=(0, 10))
        
        presets = [
            ("네이버 뉴스", self.preset_naver_news),
            ("일반 블로그", self.preset_blog),
            ("상품 목록", self.preset_products),
            ("자동 감지", self.auto_detect_selectors)
        ]
        
        for text, command in presets:
            btn = ttk.Button(preset_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=2)
        
        # 선택자 입력
        ttk.Label(selector_frame, text="CSS 선택자 (필드명: 선택자)").grid(row=1, column=0, sticky=tk.W)
        
        self.selector_text = scrolledtext.ScrolledText(selector_frame, height=6, width=60)
        self.selector_text.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # 기본값 설정
        default_selectors = """title: h1, h2, .title
content: .content, article, .post-body
date: time, .date, .timestamp
author: .author, .writer
link: a[href]"""
        self.selector_text.insert(1.0, default_selectors)
        
        # 도움말
        help_text = "예시: title: h1.article-title\n각 줄에 하나씩 입력하세요."
        help_label = ttk.Label(selector_frame, text=help_text, font=('맑은 고딕', 9), foreground='gray')
        help_label.grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        
        selector_frame.columnconfigure(0, weight=1)
        
    def create_control_buttons(self, parent):
        """컨트롤 버튼"""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        # 크롤링 시작 버튼
        self.start_btn = ttk.Button(control_frame, text="🚀 크롤링 시작", 
                                    command=self.start_crawling, style='Success.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # 중지 버튼
        self.stop_btn = ttk.Button(control_frame, text="⏹ 중지", 
                                   command=self.stop_crawling, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # CSV 저장 버튼
        self.save_btn = ttk.Button(control_frame, text="💾 CSV 저장", 
                                   command=self.save_to_csv, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # Excel 저장 버튼
        self.excel_btn = ttk.Button(control_frame, text="📊 Excel 저장", 
                                    command=self.save_to_excel, state=tk.DISABLED)
        self.excel_btn.pack(side=tk.LEFT, padx=5)
        
        # 결과 폴더 열기
        self.folder_btn = ttk.Button(control_frame, text="📁 결과 폴더", 
                                     command=self.open_results_folder)
        self.folder_btn.pack(side=tk.LEFT, padx=5)
        
    def create_progress_section(self, parent):
        """진행 상황 표시"""
        progress_frame = ttk.Frame(parent)
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.progress_label = ttk.Label(progress_frame, text="대기 중...")
        self.progress_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.progress_percent = ttk.Label(progress_frame, text="0%")
        self.progress_percent.pack(side=tk.LEFT, padx=(10, 0))
        
    def create_log_section(self, parent):
        """로그 출력"""
        log_frame = ttk.LabelFrame(parent, text="실시간 로그", padding="5")
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 로그 색상 태그
        self.log_text.tag_config('INFO', foreground='black')
        self.log_text.tag_config('SUCCESS', foreground='green')
        self.log_text.tag_config('ERROR', foreground='red')
        self.log_text.tag_config('WARNING', foreground='orange')
        
    def create_result_preview(self, parent):
        """결과 미리보기"""
        preview_frame = ttk.LabelFrame(parent, text="결과 미리보기", padding="5")
        preview_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Treeview로 테이블 생성
        columns = ('번호', '제목', '내용', 'URL')
        self.result_tree = ttk.Treeview(preview_frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=150)
        
        # 스크롤바
        v_scroll = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        h_scroll = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=self.result_tree.xview)
        self.result_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.result_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
    def create_status_bar(self):
        """상태바"""
        self.status_bar = ttk.Label(self.root, text=f"준비 완료 | {APP_NAME} v{APP_VERSION}", 
                                   relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
    # ==================== 기능 구현 ====================
    
    def log(self, message, level='INFO'):
        """로그 출력"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_message, level)
        self.log_text.see(tk.END)
        
        # 파일 로그
        with open(f"logs/crawl_{datetime.now().strftime('%Y%m%d')}.log", 'a', encoding='utf-8') as f:
            f.write(log_message)
    
    def update_status(self, message):
        """상태바 업데이트"""
        self.status_bar.config(text=f"{message} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def test_connection(self):
        """URL 연결 테스트"""
        url = self.url_var.get()
        if not url:
            messagebox.showwarning("경고", "URL을 입력하세요.")
            return
        
        try:
            self.log(f"연결 테스트 중: {url}")
            response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                self.log(f"✅ 연결 성공! (상태 코드: {response.status_code})", 'SUCCESS')
                messagebox.showinfo("성공", f"연결 성공!\n상태 코드: {response.status_code}")
            else:
                self.log(f"⚠️ 연결됨, 상태 코드: {response.status_code}", 'WARNING')
        except Exception as e:
            self.log(f"❌ 연결 실패: {str(e)}", 'ERROR')
            messagebox.showerror("오류", f"연결 실패:\n{str(e)}")
    
    def preset_naver_news(self):
        """네이버 뉴스 프리셋"""
        selectors = """title: .sa_text_title
content: .sa_text_lede
date: .sa_text_datetime
link: .sa_text_title a[href]
image: .sa_thumb_inner img[src]"""
        self.selector_text.delete(1.0, tk.END)
        self.selector_text.insert(1.0, selectors)
        self.log("네이버 뉴스 프리셋 적용", 'INFO')
        
    def preset_blog(self):
        """블로그 프리셋"""
        selectors = """title: h1, h2, .post-title
content: .post-content, .entry-content, article
author: .author, .writer, .by
date: .date, time, .published
tags: .tag, .category"""
        self.selector_text.delete(1.0, tk.END)
        self.selector_text.insert(1.0, selectors)
        self.log("블로그 프리셋 적용", 'INFO')
        
    def preset_products(self):
        """상품 목록 프리셋"""
        selectors = """name: .product-name, .item-title
price: .price, .cost, .amount
description: .description, .summary
image: .product-image img[src]
link: a.product-link[href]"""
        self.selector_text.delete(1.0, tk.END)
        self.selector_text.insert(1.0, selectors)
        self.log("상품 목록 프리셋 적용", 'INFO')
    
    def auto_detect_selectors(self):
        """자동 선택자 감지"""
        url = self.url_var.get()
        if not url:
            messagebox.showwarning("경고", "URL을 먼저 입력하세요.")
            return
        
        try:
            self.log("자동 선택자 감지 중...")
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.text, 'html.parser')
            
            selectors = []
            
            # 제목 감지
            for tag in ['h1', 'h2', '.title', '[class*="title"]']:
                if soup.select(tag):
                    selectors.append(f"title: {tag}")
                    break
            
            # 내용 감지
            for tag in ['article', '.content', 'main', '[class*="content"]']:
                if soup.select(tag):
                    selectors.append(f"content: {tag}")
                    break
            
            # 날짜 감지
            for tag in ['time', '.date', '[class*="date"]']:
                if soup.select(tag):
                    selectors.append(f"date: {tag}")
                    break
            
            # 링크와 이미지
            if soup.select('a[href]'):
                selectors.append("link: a[href]")
            if soup.select('img[src]'):
                selectors.append("image: img[src]")
            
            if selectors:
                self.selector_text.delete(1.0, tk.END)
                self.selector_text.insert(1.0, '\n'.join(selectors))
                self.log(f"✅ 자동 감지 완료: {len(selectors)}개 선택자", 'SUCCESS')
            else:
                self.log("⚠️ 자동 감지 실패, 수동 입력 필요", 'WARNING')
                
        except Exception as e:
            self.log(f"❌ 자동 감지 오류: {str(e)}", 'ERROR')
    
    def start_crawling(self):
        """크롤링 시작"""
        if self.is_crawling:
            messagebox.showwarning("경고", "이미 크롤링이 진행 중입니다.")
            return
        
        url = self.url_var.get()
        if not url:
            messagebox.showwarning("경고", "URL을 입력하세요.")
            return
        
        # 선택자 파싱
        selectors = {}
        for line in self.selector_text.get(1.0, tk.END).strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                selectors[key.strip()] = value.strip()
        
        if not selectors:
            messagebox.showwarning("경고", "CSS 선택자를 입력하세요.")
            return
        
        # UI 상태 변경
        self.is_crawling = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.DISABLED)
        self.excel_btn.config(state=tk.DISABLED)
        self.results = []
        
        # 결과 트리 초기화
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # 크롤링 스레드 시작
        self.crawl_thread = threading.Thread(
            target=self.crawl_worker,
            args=(url, selectors, self.pages_var.get(), self.delay_var.get())
        )
        self.crawl_thread.daemon = True
        self.crawl_thread.start()
    
    def crawl_worker(self, url, selectors, max_pages, delay):
        """크롤링 워커 스레드"""
        try:
            self.log(f"🚀 크롤링 시작: {url}", 'SUCCESS')
            self.update_status("크롤링 진행 중...")
            
            # 메인 페이지 크롤링
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 데이터 추출
            page_results = self.extract_data(soup, selectors, url)
            
            if page_results:
                for result in page_results:
                    self.results.append(result)
                    self.add_to_preview(result)
                self.log(f"📄 메인 페이지: {len(page_results)}개 항목 수집", 'SUCCESS')
            
            # 추가 페이지 크롤링 (링크 찾기)
            if max_pages > 1:
                links = self.find_links(soup, url)
                total_links = min(len(links), max_pages - 1)
                
                for i, link in enumerate(links[:total_links]):
                    if not self.is_crawling:
                        break
                    
                    # 진행률 업데이트
                    progress = int(((i + 2) / (total_links + 1)) * 100)
                    self.progress_bar['value'] = progress
                    self.progress_percent.config(text=f"{progress}%")
                    self.progress_label.config(text=f"페이지 {i+2}/{total_links+1} 크롤링 중...")
                    
                    try:
                        time.sleep(delay)  # 지연
                        response = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        page_results = self.extract_data(soup, selectors, link)
                        if page_results:
                            for result in page_results:
                                self.results.append(result)
                                self.add_to_preview(result)
                            self.log(f"📄 페이지 {i+2}: {len(page_results)}개 항목", 'INFO')
                    except Exception as e:
                        self.log(f"⚠️ 페이지 크롤링 실패: {link[:50]}... - {str(e)}", 'WARNING')
            
            # 완료
            self.progress_bar['value'] = 100
            self.progress_percent.config(text="100%")
            self.progress_label.config(text=f"완료! 총 {len(self.results)}개 항목 수집")
            self.log(f"✅ 크롤링 완료! 총 {len(self.results)}개 항목 수집", 'SUCCESS')
            self.update_status(f"크롤링 완료 - {len(self.results)}개 항목")
            
            # 자동 저장
            if self.results:
                self.auto_save()
            
        except Exception as e:
            self.log(f"❌ 크롤링 오류: {str(e)}", 'ERROR')
            messagebox.showerror("오류", f"크롤링 중 오류 발생:\n{str(e)}")
        finally:
            self.is_crawling = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            if self.results:
                self.save_btn.config(state=tk.NORMAL)
                self.excel_btn.config(state=tk.NORMAL)
    
    def extract_data(self, soup, selectors, url):
        """데이터 추출"""
        results = []
        
        # 각 선택자별로 요소 찾기
        extracted = {}
        max_items = 0
        
        for field, selector in selectors.items():
            elements = soup.select(selector)
            if elements:
                extracted[field] = [el.get_text(strip=True) for el in elements]
                max_items = max(max_items, len(extracted[field]))
        
        # 결과 정리
        for i in range(max_items):
            item = {'url': url, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            for field, values in extracted.items():
                if i < len(values):
                    item[field] = values[i]
                else:
                    item[field] = ''
            results.append(item)
        
        return results[:50]  # 최대 50개만
    
    def find_links(self, soup, base_url):
        """페이지 내 링크 찾기"""
        links = []
        parsed_base = urlparse(base_url)
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            
            # 같은 도메인만
            if parsed.netloc == parsed_base.netloc:
                if full_url not in links and full_url != base_url:
                    links.append(full_url)
        
        return links[:20]  # 최대 20개
    
    def add_to_preview(self, result):
        """미리보기에 추가"""
        # 주요 필드만 표시
        values = (
            len(self.result_tree.get_children()) + 1,
            result.get('title', result.get('name', ''))[:50],
            result.get('content', result.get('description', ''))[:50],
            result.get('url', '')[:50]
        )
        self.result_tree.insert('', tk.END, values=values)
    
    def stop_crawling(self):
        """크롤링 중지"""
        self.is_crawling = False
        self.log("⏹ 사용자가 크롤링을 중지했습니다.", 'WARNING')
        self.update_status("크롤링 중지됨")
    
    def auto_save(self):
        """자동 저장"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"results/crawl_{timestamp}_auto.csv"
        
        df = pd.DataFrame(self.results)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        self.log(f"💾 자동 저장 완료: {filename}", 'SUCCESS')
    
    def save_to_csv(self):
        """CSV로 저장"""
        if not self.results:
            messagebox.showwarning("경고", "저장할 데이터가 없습니다.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV 파일", "*.csv"), ("모든 파일", "*.*")],
            initialdir="results",
            initialfile=f"crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            try:
                df = pd.DataFrame(self.results)
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                self.log(f"✅ CSV 저장 완료: {filename}", 'SUCCESS')
                messagebox.showinfo("성공", f"CSV 파일이 저장되었습니다.\n{filename}")
                
                # 폴더 열기 옵션
                if messagebox.askyesno("확인", "저장된 폴더를 열까요?"):
                    os.startfile(os.path.dirname(filename))
            except Exception as e:
                self.log(f"❌ 저장 실패: {str(e)}", 'ERROR')
                messagebox.showerror("오류", f"저장 실패:\n{str(e)}")
    
    def save_to_excel(self):
        """Excel로 저장"""
        if not self.results:
            messagebox.showwarning("경고", "저장할 데이터가 없습니다.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel 파일", "*.xlsx"), ("모든 파일", "*.*")],
            initialdir="results",
            initialfile=f"crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        
        if filename:
            try:
                df = pd.DataFrame(self.results)
                
                # 스타일 적용하여 저장
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='크롤링 결과')
                    
                    # 스타일 적용
                    workbook = writer.book
                    worksheet = writer.sheets['크롤링 결과']
                    
                    # 헤더 스타일
                    from openpyxl.styles import PatternFill, Font, Alignment
                    header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
                    header_font = Font(color='FFFFFF', bold=True)
                    
                    for cell in worksheet[1]:
                        cell.fill = header_fill
                        cell.font = header_font
                        cell.alignment = Alignment(horizontal='center')
                    
                    # 열 너비 자동 조정
                    for column in worksheet.columns:
                        max_length = 0
                        column = [cell for cell in column]
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
                
                self.log(f"✅ Excel 저장 완료: {filename}", 'SUCCESS')
                messagebox.showinfo("성공", f"Excel 파일이 저장되었습니다.\n{filename}")
                
                # 파일 열기 옵션
                if messagebox.askyesno("확인", "Excel 파일을 열까요?"):
                    os.startfile(filename)
            except Exception as e:
                self.log(f"❌ 저장 실패: {str(e)}", 'ERROR')
                messagebox.showerror("오류", f"저장 실패:\n{str(e)}")
    
    def open_results_folder(self):
        """결과 폴더 열기"""
        results_path = os.path.abspath("results")
        if os.path.exists(results_path):
            os.startfile(results_path)
        else:
            os.makedirs(results_path)
            os.startfile(results_path)


def main():
    """메인 함수"""
    root = tk.Tk()
    app = CrawlerGUI(root)
    
    # 종료 시 확인
    def on_closing():
        if app.is_crawling:
            if messagebox.askokcancel("종료", "크롤링이 진행 중입니다. 종료하시겠습니까?"):
                app.is_crawling = False
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()