#!/usr/bin/env python3
"""
크롤링 툴 UI 컴포넌트 구현 예제
Tkinter (Desktop) + Flask/React (Web) 버전
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import json
import time
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional, Callable
import os


# ==================== Desktop UI (Tkinter) ====================

class ModernUI:
    """모던한 UI 스타일 정의"""
    
    # 색상 팔레트
    COLORS = {
        'primary': '#2563EB',
        'primary_dark': '#1E40AF',
        'success': '#10B981',
        'warning': '#F59E0B',
        'error': '#EF4444',
        'bg': '#F9FAFB',
        'card': '#FFFFFF',
        'text': '#111827',
        'text_secondary': '#6B7280',
        'border': '#E5E7EB'
    }
    
    # 폰트 설정
    FONTS = {
        'heading': ('Helvetica', 16, 'bold'),
        'subheading': ('Helvetica', 12, 'bold'),
        'body': ('Helvetica', 10),
        'small': ('Helvetica', 9),
        'mono': ('Courier', 10)
    }


class StatusCard(tk.Frame):
    """상태 표시 카드 컴포넌트"""
    
    def __init__(self, parent, title="", value="", icon="📊", **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(
            bg=ModernUI.COLORS['card'],
            relief=tk.FLAT,
            borderwidth=1,
            highlightbackground=ModernUI.COLORS['border'],
            highlightthickness=1
        )
        
        # 패딩
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        inner_frame = tk.Frame(self, bg=ModernUI.COLORS['card'])
        inner_frame.grid(row=0, column=0, padx=15, pady=15)
        
        # 아이콘
        icon_label = tk.Label(
            inner_frame,
            text=icon,
            font=('Helvetica', 24),
            bg=ModernUI.COLORS['card']
        )
        icon_label.grid(row=0, column=0, rowspan=2, padx=(0, 10))
        
        # 값
        self.value_label = tk.Label(
            inner_frame,
            text=value,
            font=ModernUI.FONTS['heading'],
            bg=ModernUI.COLORS['card'],
            fg=ModernUI.COLORS['text']
        )
        self.value_label.grid(row=0, column=1, sticky='w')
        
        # 제목
        title_label = tk.Label(
            inner_frame,
            text=title,
            font=ModernUI.FONTS['small'],
            bg=ModernUI.COLORS['card'],
            fg=ModernUI.COLORS['text_secondary']
        )
        title_label.grid(row=1, column=1, sticky='w')
    
    def update_value(self, value):
        """값 업데이트"""
        self.value_label.config(text=value)


class ProgressCard(tk.Frame):
    """진행률 표시 카드"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg=ModernUI.COLORS['card'])
        
        # 제목
        self.title_label = tk.Label(
            self,
            text="크롤링 진행 상황",
            font=ModernUI.FONTS['subheading'],
            bg=ModernUI.COLORS['card']
        )
        self.title_label.pack(pady=(10, 5))
        
        # 진행률 바
        self.progress = ttk.Progressbar(
            self,
            length=400,
            mode='determinate',
            style='Modern.Horizontal.TProgressbar'
        )
        self.progress.pack(pady=5)
        
        # 상태 텍스트
        self.status_label = tk.Label(
            self,
            text="대기 중...",
            font=ModernUI.FONTS['body'],
            bg=ModernUI.COLORS['card'],
            fg=ModernUI.COLORS['text_secondary']
        )
        self.status_label.pack(pady=5)
        
        # 통계
        stats_frame = tk.Frame(self, bg=ModernUI.COLORS['card'])
        stats_frame.pack(pady=10)
        
        self.stats = {
            'collected': tk.Label(stats_frame, text="수집: 0", font=ModernUI.FONTS['small']),
            'failed': tk.Label(stats_frame, text="실패: 0", font=ModernUI.FONTS['small']),
            'remaining': tk.Label(stats_frame, text="남음: 0", font=ModernUI.FONTS['small'])
        }
        
        for idx, (key, label) in enumerate(self.stats.items()):
            label.configure(bg=ModernUI.COLORS['card'])
            label.grid(row=0, column=idx, padx=10)
    
    def update(self, progress=0, status="", collected=0, failed=0, remaining=0):
        """진행 상황 업데이트"""
        self.progress['value'] = progress
        self.status_label.config(text=status)
        self.stats['collected'].config(text=f"수집: {collected}")
        self.stats['failed'].config(text=f"실패: {failed}")
        self.stats['remaining'].config(text=f"남음: {remaining}")


class CrawlerSetupWizard(tk.Toplevel):
    """크롤링 설정 마법사"""
    
    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.title("새 크롤링 작업")
        self.geometry("600x500")
        self.configure(bg=ModernUI.COLORS['bg'])
        
        # 데이터 저장
        self.config = {
            'name': '',
            'url': '',
            'selectors': [],
            'interval': 60,
            'output_format': 'csv'
        }
        
        # 현재 스텝
        self.current_step = 0
        self.steps = [
            self.create_step1,
            self.create_step2,
            self.create_step3
        ]
        
        # 메인 프레임
        self.main_frame = tk.Frame(self, bg=ModernUI.COLORS['bg'])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 스텝 표시
        self.step_indicator = tk.Label(
            self.main_frame,
            text="Step 1 / 3",
            font=ModernUI.FONTS['subheading'],
            bg=ModernUI.COLORS['bg']
        )
        self.step_indicator.pack(pady=(0, 20))
        
        # 스텝 콘텐츠 프레임
        self.content_frame = tk.Frame(self.main_frame, bg=ModernUI.COLORS['bg'])
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 버튼 프레임
        button_frame = tk.Frame(self.main_frame, bg=ModernUI.COLORS['bg'])
        button_frame.pack(side=tk.BOTTOM, pady=(20, 0))
        
        self.prev_btn = tk.Button(
            button_frame,
            text="이전",
            command=self.prev_step,
            state=tk.DISABLED
        )
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = tk.Button(
            button_frame,
            text="다음",
            command=self.next_step
        )
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        # 첫 스텝 표시
        self.show_step()
    
    def create_step1(self):
        """Step 1: 기본 정보"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        tk.Label(
            self.content_frame,
            text="기본 정보",
            font=ModernUI.FONTS['heading'],
            bg=ModernUI.COLORS['bg']
        ).pack(pady=(0, 20))
        
        # 작업 이름
        tk.Label(
            self.content_frame,
            text="작업 이름",
            font=ModernUI.FONTS['body'],
            bg=ModernUI.COLORS['bg']
        ).pack(anchor='w', pady=(10, 5))
        
        self.name_entry = tk.Entry(
            self.content_frame,
            font=ModernUI.FONTS['body'],
            width=50
        )
        self.name_entry.pack(fill=tk.X)
        self.name_entry.insert(0, self.config['name'])
        
        # URL
        tk.Label(
            self.content_frame,
            text="대상 URL",
            font=ModernUI.FONTS['body'],
            bg=ModernUI.COLORS['bg']
        ).pack(anchor='w', pady=(20, 5))
        
        self.url_entry = tk.Entry(
            self.content_frame,
            font=ModernUI.FONTS['body'],
            width=50
        )
        self.url_entry.pack(fill=tk.X)
        self.url_entry.insert(0, self.config['url'])
    
    def create_step2(self):
        """Step 2: 데이터 선택"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        tk.Label(
            self.content_frame,
            text="데이터 선택",
            font=ModernUI.FONTS['heading'],
            bg=ModernUI.COLORS['bg']
        ).pack(pady=(0, 20))
        
        # CSS 선택자 입력
        tk.Label(
            self.content_frame,
            text="CSS 선택자 (한 줄에 하나씩)",
            font=ModernUI.FONTS['body'],
            bg=ModernUI.COLORS['bg']
        ).pack(anchor='w', pady=(10, 5))
        
        self.selector_text = scrolledtext.ScrolledText(
            self.content_frame,
            height=10,
            font=ModernUI.FONTS['mono']
        )
        self.selector_text.pack(fill=tk.BOTH, expand=True)
        
        # 예제 표시
        example = """예제:
h1.title - 제목
div.content p - 본문
span.author - 작성자
time.date - 날짜"""
        self.selector_text.insert('1.0', example)
    
    def create_step3(self):
        """Step 3: 스케줄 설정"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        tk.Label(
            self.content_frame,
            text="스케줄 설정",
            font=ModernUI.FONTS['heading'],
            bg=ModernUI.COLORS['bg']
        ).pack(pady=(0, 20))
        
        # 실행 간격
        tk.Label(
            self.content_frame,
            text="실행 간격 (분)",
            font=ModernUI.FONTS['body'],
            bg=ModernUI.COLORS['bg']
        ).pack(anchor='w', pady=(10, 5))
        
        interval_frame = tk.Frame(self.content_frame, bg=ModernUI.COLORS['bg'])
        interval_frame.pack(anchor='w')
        
        self.interval_var = tk.IntVar(value=self.config['interval'])
        self.interval_scale = tk.Scale(
            interval_frame,
            from_=1,
            to=1440,
            orient=tk.HORIZONTAL,
            variable=self.interval_var,
            length=300
        )
        self.interval_scale.pack(side=tk.LEFT)
        
        self.interval_label = tk.Label(
            interval_frame,
            text=f"{self.interval_var.get()}분",
            font=ModernUI.FONTS['body'],
            bg=ModernUI.COLORS['bg']
        )
        self.interval_label.pack(side=tk.LEFT, padx=10)
        
        self.interval_var.trace('w', lambda *args: self.interval_label.config(
            text=f"{self.interval_var.get()}분"
        ))
        
        # 출력 형식
        tk.Label(
            self.content_frame,
            text="출력 형식",
            font=ModernUI.FONTS['body'],
            bg=ModernUI.COLORS['bg']
        ).pack(anchor='w', pady=(30, 5))
        
        self.format_var = tk.StringVar(value=self.config['output_format'])
        
        formats = ['CSV', 'JSON', 'Excel']
        for fmt in formats:
            tk.Radiobutton(
                self.content_frame,
                text=fmt,
                variable=self.format_var,
                value=fmt.lower(),
                font=ModernUI.FONTS['body'],
                bg=ModernUI.COLORS['bg']
            ).pack(anchor='w')
    
    def show_step(self):
        """현재 스텝 표시"""
        self.step_indicator.config(text=f"Step {self.current_step + 1} / 3")
        self.steps[self.current_step]()
        
        # 버튼 상태 업데이트
        self.prev_btn.config(state=tk.NORMAL if self.current_step > 0 else tk.DISABLED)
        self.next_btn.config(text="완료" if self.current_step == 2 else "다음")
    
    def prev_step(self):
        """이전 스텝"""
        self.save_current_step()
        if self.current_step > 0:
            self.current_step -= 1
            self.show_step()
    
    def next_step(self):
        """다음 스텝"""
        self.save_current_step()
        if self.current_step < 2:
            self.current_step += 1
            self.show_step()
        else:
            self.finish()
    
    def save_current_step(self):
        """현재 스텝 데이터 저장"""
        if self.current_step == 0:
            self.config['name'] = self.name_entry.get()
            self.config['url'] = self.url_entry.get()
        elif self.current_step == 1:
            text = self.selector_text.get('1.0', tk.END)
            self.config['selectors'] = [
                line.strip() for line in text.split('\n')
                if line.strip() and not line.startswith('예제:')
            ]
        elif self.current_step == 2:
            self.config['interval'] = self.interval_var.get()
            self.config['output_format'] = self.format_var.get()
    
    def finish(self):
        """완료"""
        if self.callback:
            self.callback(self.config)
        self.destroy()


class CrawlerDashboard(tk.Tk):
    """메인 대시보드"""
    
    def __init__(self):
        super().__init__()
        self.title("CrawlMaster Pro - 대시보드")
        self.geometry("1200x700")
        self.configure(bg=ModernUI.COLORS['bg'])
        
        # 스타일 설정
        self.setup_styles()
        
        # 메뉴바
        self.create_menubar()
        
        # 헤더
        self.create_header()
        
        # 메인 콘텐츠
        self.create_main_content()
        
        # 상태바
        self.create_statusbar()
        
        # 데이터
        self.jobs = []
        self.update_stats()
    
    def setup_styles(self):
        """TTK 스타일 설정"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 진행바 스타일
        style.configure(
            'Modern.Horizontal.TProgressbar',
            background=ModernUI.COLORS['primary'],
            troughcolor=ModernUI.COLORS['border'],
            borderwidth=0,
            lightcolor=ModernUI.COLORS['primary'],
            darkcolor=ModernUI.COLORS['primary']
        )
    
    def create_menubar(self):
        """메뉴바 생성"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # 파일 메뉴
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="파일", menu=file_menu)
        file_menu.add_command(label="새 작업", command=self.new_job)
        file_menu.add_command(label="작업 불러오기", command=self.load_job)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.quit)
        
        # 도구 메뉴
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="도구", menu=tools_menu)
        tools_menu.add_command(label="프록시 설정")
        tools_menu.add_command(label="브라우저 설정")
        
        # 도움말 메뉴
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="도움말", menu=help_menu)
        help_menu.add_command(label="사용 가이드")
        help_menu.add_command(label="정보", command=self.show_about)
    
    def create_header(self):
        """헤더 생성"""
        header = tk.Frame(self, bg=ModernUI.COLORS['primary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # 로고/타이틀
        title = tk.Label(
            header,
            text="🕷️ CrawlMaster Pro",
            font=('Helvetica', 20, 'bold'),
            bg=ModernUI.COLORS['primary'],
            fg='white'
        )
        title.pack(side=tk.LEFT, padx=20, pady=15)
        
        # 액션 버튼
        btn_frame = tk.Frame(header, bg=ModernUI.COLORS['primary'])
        btn_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        new_btn = tk.Button(
            btn_frame,
            text="➕ 새 작업",
            command=self.new_job,
            bg='white',
            fg=ModernUI.COLORS['primary'],
            font=ModernUI.FONTS['body'],
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        new_btn.pack(side=tk.LEFT, padx=5)
    
    def create_main_content(self):
        """메인 콘텐츠 영역"""
        main = tk.Frame(self, bg=ModernUI.COLORS['bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 상단 통계 카드
        stats_frame = tk.Frame(main, bg=ModernUI.COLORS['bg'])
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.stat_cards = {
            'active': StatusCard(stats_frame, "활성 작업", "0", "🔄"),
            'completed': StatusCard(stats_frame, "완료됨", "0", "✅"),
            'data': StatusCard(stats_frame, "수집 데이터", "0", "📊"),
            'errors': StatusCard(stats_frame, "에러", "0", "⚠️")
        }
        
        for idx, card in enumerate(self.stat_cards.values()):
            card.grid(row=0, column=idx, padx=5, sticky='ew')
            stats_frame.grid_columnconfigure(idx, weight=1)
        
        # 중간 영역 (왼쪽: 진행상황, 오른쪽: 로그)
        middle_frame = tk.Frame(main, bg=ModernUI.COLORS['bg'])
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 진행상황
        progress_frame = tk.Frame(middle_frame, bg=ModernUI.COLORS['card'])
        progress_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.progress_card = ProgressCard(progress_frame)
        self.progress_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 로그
        log_frame = tk.Frame(middle_frame, bg=ModernUI.COLORS['card'])
        log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(
            log_frame,
            text="실시간 로그",
            font=ModernUI.FONTS['subheading'],
            bg=ModernUI.COLORS['card']
        ).pack(pady=10)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            font=ModernUI.FONTS['mono'],
            bg='#1F2937',
            fg='#10B981',
            insertbackground='#10B981'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 하단 작업 목록
        jobs_frame = tk.Frame(main, bg=ModernUI.COLORS['card'])
        jobs_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            jobs_frame,
            text="작업 목록",
            font=ModernUI.FONTS['subheading'],
            bg=ModernUI.COLORS['card']
        ).pack(pady=10)
        
        # 테이블
        columns = ('이름', 'URL', '상태', '진행률', '마지막 실행')
        self.job_tree = ttk.Treeview(jobs_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.job_tree.heading(col, text=col)
            self.job_tree.column(col, width=200)
        
        self.job_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(jobs_frame, orient=tk.VERTICAL, command=self.job_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.job_tree.configure(yscrollcommand=scrollbar.set)
    
    def create_statusbar(self):
        """상태바 생성"""
        statusbar = tk.Frame(self, bg=ModernUI.COLORS['border'], height=30)
        statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(
            statusbar,
            text="준비",
            font=ModernUI.FONTS['small'],
            bg=ModernUI.COLORS['border']
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # 시스템 정보
        self.system_label = tk.Label(
            statusbar,
            text="CPU: 0% | 메모리: 0MB",
            font=ModernUI.FONTS['small'],
            bg=ModernUI.COLORS['border']
        )
        self.system_label.pack(side=tk.RIGHT, padx=10)
    
    def new_job(self):
        """새 작업 생성"""
        wizard = CrawlerSetupWizard(self, callback=self.add_job)
    
    def add_job(self, config):
        """작업 추가"""
        job = {
            'id': len(self.jobs) + 1,
            'name': config['name'],
            'url': config['url'],
            'status': '대기',
            'progress': 0,
            'last_run': '-'
        }
        self.jobs.append(job)
        
        # 테이블에 추가
        self.job_tree.insert('', tk.END, values=(
            job['name'],
            job['url'][:50] + '...' if len(job['url']) > 50 else job['url'],
            job['status'],
            f"{job['progress']}%",
            job['last_run']
        ))
        
        # 로그
        self.log(f"새 작업 생성: {job['name']}")
        self.update_stats()
        
        # 시뮬레이션 시작
        threading.Thread(target=self.simulate_crawling, args=(job,), daemon=True).start()
    
    def simulate_crawling(self, job):
        """크롤링 시뮬레이션"""
        job['status'] = '실행 중'
        self.log(f"크롤링 시작: {job['name']}")
        
        for i in range(101):
            job['progress'] = i
            self.progress_card.update(
                progress=i,
                status=f"{job['name']} 크롤링 중...",
                collected=i * 10,
                failed=i // 20,
                remaining=1000 - (i * 10)
            )
            time.sleep(0.1)
        
        job['status'] = '완료'
        job['last_run'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.log(f"크롤링 완료: {job['name']}")
        self.update_stats()
    
    def load_job(self):
        """작업 불러오기"""
        filename = filedialog.askopenfilename(
            title="작업 파일 선택",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.add_job(config)
    
    def update_stats(self):
        """통계 업데이트"""
        active = sum(1 for j in self.jobs if j['status'] == '실행 중')
        completed = sum(1 for j in self.jobs if j['status'] == '완료')
        
        self.stat_cards['active'].update_value(str(active))
        self.stat_cards['completed'].update_value(str(completed))
        self.stat_cards['data'].update_value("12.5K")
        self.stat_cards['errors'].update_value("3")
    
    def log(self, message):
        """로그 출력"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def show_about(self):
        """정보 다이얼로그"""
        messagebox.showinfo(
            "CrawlMaster Pro",
            "CrawlMaster Pro v1.0.0\n\n"
            "강력한 웹 크롤링 도구\n\n"
            "© 2025 CrawlMaster Inc."
        )


# ==================== Web UI (Flask + HTML/JS) ====================

WEB_UI_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CrawlMaster Pro - Web Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --primary: #2563EB;
            --primary-dark: #1E40AF;
            --success: #10B981;
            --warning: #F59E0B;
            --error: #EF4444;
            --bg: #F9FAFB;
            --card: #FFFFFF;
            --text: #111827;
            --text-secondary: #6B7280;
            --border: #E5E7EB;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
        }
        
        /* Header */
        .header {
            background: var(--primary);
            color: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .btn-primary {
            background: white;
            color: var(--primary);
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }
        
        /* Container */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: var(--card);
            padding: 1.5rem;
            border-radius: 0.5rem;
            border: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 1rem;
            transition: transform 0.2s;
        }
        
        .stat-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .stat-icon {
            font-size: 2rem;
        }
        
        .stat-content {
            flex: 1;
        }
        
        .stat-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--text);
        }
        
        .stat-label {
            font-size: 0.875rem;
            color: var(--text-secondary);
        }
        
        /* Progress Card */
        .progress-card {
            background: var(--card);
            padding: 1.5rem;
            border-radius: 0.5rem;
            border: 1px solid var(--border);
            margin-bottom: 2rem;
        }
        
        .progress-bar {
            width: 100%;
            height: 2rem;
            background: var(--border);
            border-radius: 1rem;
            overflow: hidden;
            margin: 1rem 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary) 0%, var(--primary-dark) 100%);
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        /* Table */
        .table-card {
            background: var(--card);
            border-radius: 0.5rem;
            border: 1px solid var(--border);
            overflow: hidden;
        }
        
        .table-header {
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--border);
            font-weight: 600;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th {
            text-align: left;
            padding: 0.75rem 1.5rem;
            background: var(--bg);
            font-weight: 500;
            color: var(--text-secondary);
            font-size: 0.875rem;
        }
        
        td {
            padding: 0.75rem 1.5rem;
            border-top: 1px solid var(--border);
        }
        
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .status-running {
            background: rgba(245, 158, 11, 0.1);
            color: var(--warning);
        }
        
        .status-completed {
            background: rgba(16, 185, 129, 0.1);
            color: var(--success);
        }
        
        .status-failed {
            background: rgba(239, 68, 68, 0.1);
            color: var(--error);
        }
        
        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        
        .modal.active {
            display: flex;
        }
        
        .modal-content {
            background: var(--card);
            padding: 2rem;
            border-radius: 0.5rem;
            width: 90%;
            max-width: 500px;
            max-height: 90vh;
            overflow-y: auto;
        }
        
        .modal-header {
            margin-bottom: 1.5rem;
        }
        
        .modal-title {
            font-size: 1.25rem;
            font-weight: 600;
        }
        
        .form-group {
            margin-bottom: 1rem;
        }
        
        .form-label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            font-size: 0.875rem;
        }
        
        .form-input {
            width: 100%;
            padding: 0.5rem;
            border: 1px solid var(--border);
            border-radius: 0.375rem;
            font-size: 1rem;
        }
        
        .form-input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }
        
        .modal-footer {
            display: flex;
            justify-content: flex-end;
            gap: 0.5rem;
            margin-top: 1.5rem;
        }
        
        .btn {
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            border: none;
        }
        
        .btn-secondary {
            background: var(--bg);
            color: var(--text);
        }
        
        .btn-primary {
            background: var(--primary);
            color: white;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            table {
                font-size: 0.875rem;
            }
            
            th, td {
                padding: 0.5rem;
            }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header class="header">
        <h1>
            <span>🕷️</span>
            CrawlMaster Pro
        </h1>
        <button class="btn-primary" onclick="openModal()">
            ➕ 새 작업
        </button>
    </header>
    
    <!-- Main Content -->
    <div class="container">
        <!-- Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">🔄</div>
                <div class="stat-content">
                    <div class="stat-value" id="active-jobs">3</div>
                    <div class="stat-label">활성 작업</div>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">✅</div>
                <div class="stat-content">
                    <div class="stat-value" id="completed-jobs">127</div>
                    <div class="stat-label">완료된 작업</div>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-content">
                    <div class="stat-value" id="total-data">45.2K</div>
                    <div class="stat-label">수집된 데이터</div>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">⚠️</div>
                <div class="stat-content">
                    <div class="stat-value" id="error-count">2</div>
                    <div class="stat-label">에러</div>
                </div>
            </div>
        </div>
        
        <!-- Progress -->
        <div class="progress-card">
            <h2>현재 진행 중</h2>
            <div class="progress-bar">
                <div class="progress-fill" id="progress" style="width: 65%">
                    65%
                </div>
            </div>
            <p id="progress-status">네이버 뉴스 크롤링 중... (650/1000)</p>
        </div>
        
        <!-- Jobs Table -->
        <div class="table-card">
            <div class="table-header">
                <h2>작업 목록</h2>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>작업명</th>
                        <th>URL</th>
                        <th>상태</th>
                        <th>진행률</th>
                        <th>마지막 실행</th>
                        <th>액션</th>
                    </tr>
                </thead>
                <tbody id="jobs-table">
                    <tr>
                        <td>네이버 뉴스</td>
                        <td>news.naver.com</td>
                        <td><span class="status-badge status-running">실행 중</span></td>
                        <td>65%</td>
                        <td>2025-08-20 14:30</td>
                        <td>
                            <button class="btn btn-sm">일시정지</button>
                            <button class="btn btn-sm">상세</button>
                        </td>
                    </tr>
                    <tr>
                        <td>쿠팡 상품</td>
                        <td>coupang.com</td>
                        <td><span class="status-badge status-completed">완료</span></td>
                        <td>100%</td>
                        <td>2025-08-20 13:15</td>
                        <td>
                            <button class="btn btn-sm">다시 실행</button>
                            <button class="btn btn-sm">상세</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <!-- Modal -->
    <div class="modal" id="newJobModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-title">새 크롤링 작업</h2>
            </div>
            
            <form id="newJobForm">
                <div class="form-group">
                    <label class="form-label">작업 이름</label>
                    <input type="text" class="form-input" placeholder="예: 네이버 뉴스 수집" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">대상 URL</label>
                    <input type="url" class="form-input" placeholder="https://example.com" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">실행 주기</label>
                    <select class="form-input">
                        <option>1시간마다</option>
                        <option>6시간마다</option>
                        <option>매일</option>
                        <option>매주</option>
                    </select>
                </div>
                
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeModal()">취소</button>
                    <button type="submit" class="btn btn-primary">생성</button>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        // Modal Control
        function openModal() {
            document.getElementById('newJobModal').classList.add('active');
        }
        
        function closeModal() {
            document.getElementById('newJobModal').classList.remove('active');
        }
        
        // Form Submit
        document.getElementById('newJobForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // API 호출 시뮬레이션
            console.log('새 작업 생성');
            closeModal();
            
            // 토스트 알림
            showToast('작업이 생성되었습니다');
        });
        
        // Toast Notification
        function showToast(message) {
            const toast = document.createElement('div');
            toast.style.cssText = `
                position: fixed;
                bottom: 2rem;
                right: 2rem;
                background: var(--success);
                color: white;
                padding: 1rem 1.5rem;
                border-radius: 0.5rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 2000;
                animation: slideIn 0.3s ease;
            `;
            toast.textContent = message;
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.remove();
            }, 3000);
        }
        
        // Real-time Updates (WebSocket simulation)
        setInterval(() => {
            // 진행률 업데이트
            const progress = Math.min(100, parseInt(document.getElementById('progress').style.width) + 1);
            document.getElementById('progress').style.width = progress + '%';
            document.getElementById('progress').textContent = progress + '%';
            
            // 통계 업데이트
            if (Math.random() > 0.8) {
                const dataCount = document.getElementById('total-data');
                const current = parseFloat(dataCount.textContent);
                dataCount.textContent = (current + 0.1).toFixed(1) + 'K';
            }
        }, 1000);
        
        // Dark Mode Toggle
        function toggleDarkMode() {
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
        }
        
        // Load Dark Mode Preference
        if (localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
        }
    </script>
</body>
</html>
"""

# Flask 서버 예제
FLASK_SERVER = """
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template_string(WEB_UI_TEMPLATE)

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    # 작업 목록 반환
    jobs = [
        {
            'id': 1,
            'name': '네이버 뉴스',
            'url': 'https://news.naver.com',
            'status': 'running',
            'progress': 65
        }
    ]
    return jsonify(jobs)

@app.route('/api/jobs', methods=['POST'])
def create_job():
    # 새 작업 생성
    data = request.json
    # 크롤링 작업 큐에 추가
    return jsonify({'success': True, 'job_id': 123})

@app.route('/api/jobs/<int:job_id>/start', methods=['POST'])
def start_job(job_id):
    # 작업 시작
    return jsonify({'success': True})

@app.route('/api/jobs/<int:job_id>/stop', methods=['POST'])
def stop_job(job_id):
    # 작업 중지
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
"""


def main():
    """데스크톱 UI 실행"""
    app = CrawlerDashboard()
    app.mainloop()


if __name__ == "__main__":
    main()