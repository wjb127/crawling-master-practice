#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏭 크롤링 툴 공장 (Crawler Factory System)
고객 요청사항을 입력하면 맞춤형 크롤링 툴을 자동 생성하는 시스템
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Any
import re

class CrawlerFactory:
    """크롤링 툴 자동 생성 공장"""
    
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.template_path = os.path.join(self.base_path, "templates")
        self.output_path = os.path.join(self.base_path, "generated")
        
        # 출력 디렉토리 생성
        os.makedirs(self.output_path, exist_ok=True)
        
    def create_custom_crawler(self, customer_request: Dict[str, Any]) -> str:
        """고객 요청사항에 따른 맞춤형 크롤러 생성"""
        
        # 프로젝트 설정
        project_name = customer_request.get('project_name', 'CustomCrawler')
        safe_name = re.sub(r'[^a-zA-Z0-9]', '', project_name)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        project_dir = os.path.join(self.output_path, f"{safe_name}_{timestamp}")
        
        # 프로젝트 디렉토리 생성
        os.makedirs(project_dir, exist_ok=True)
        
        # 1. 메인 크롤러 생성
        self._generate_main_crawler(project_dir, customer_request)
        
        # 2. GUI 인터페이스 생성
        self._generate_gui(project_dir, customer_request)
        
        # 3. 프리셋 설정 생성
        self._generate_presets(project_dir, customer_request)
        
        # 4. 빌드 스크립트 생성
        self._generate_build_scripts(project_dir, customer_request)
        
        # 5. 인스톨러 스크립트 생성
        self._generate_installer(project_dir, customer_request)
        
        # 6. 문서 생성
        self._generate_documentation(project_dir, customer_request)
        
        # 7. 아이콘 및 리소스 생성
        self._generate_resources(project_dir, customer_request)
        
        print(f"✅ 크롤러 생성 완료: {project_dir}")
        return project_dir
    
    def _generate_main_crawler(self, project_dir: str, request: Dict):
        """메인 크롤러 엔진 생성"""
        
        crawler_code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{request.get('company_name', '고객사')} 맞춤형 크롤링 툴
{request.get('description', '웹 데이터 수집 자동화 도구')}
Version: {request.get('version', '1.0.0')}
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from datetime import datetime
import os

class {request.get('class_name', 'CustomCrawler')}:
    """맞춤형 크롤러 엔진"""
    
    def __init__(self):
        self.name = "{request.get('project_name', 'Custom Crawler')}"
        self.version = "{request.get('version', '1.0.0')}"
        self.target_sites = {json.dumps(request.get('target_sites', []), ensure_ascii=False)}
        self.data_fields = {json.dumps(request.get('data_fields', {}), ensure_ascii=False)}
        self.results = []
        
    def crawl(self, url, selectors=None):
        """크롤링 실행"""
        try:
            # 커스텀 헤더
            headers = {{
                'User-Agent': '{request.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')}',
                'Accept-Language': '{request.get('language', 'ko-KR,ko;q=0.9,en;q=0.8')}'
            }}
            
            # 요청 전송
            response = requests.get(url, headers=headers, timeout=30)
            response.encoding = 'utf-8'
            
            # HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 데이터 추출
            if not selectors:
                selectors = self.data_fields
            
            extracted_data = {{}}
            for field, selector in selectors.items():
                try:
                    elements = soup.select(selector)
                    if elements:
                        if len(elements) == 1:
                            extracted_data[field] = elements[0].get_text(strip=True)
                        else:
                            extracted_data[field] = [el.get_text(strip=True) for el in elements[:50]]
                    else:
                        extracted_data[field] = ""
                except Exception as e:
                    extracted_data[field] = f"Error: {{str(e)}}"
            
            extracted_data['url'] = url
            extracted_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            self.results.append(extracted_data)
            return extracted_data
            
        except Exception as e:
            print(f"크롤링 오류: {{str(e)}}")
            return None
    
    def save_to_csv(self, filename=None):
        """CSV로 저장"""
        if not filename:
            filename = f"{{self.name}}_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}.csv"
        
        df = pd.DataFrame(self.results)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        return filename
    
    def save_to_excel(self, filename=None):
        """Excel로 저장"""
        if not filename:
            filename = f"{{self.name}}_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}.xlsx"
        
        df = pd.DataFrame(self.results)
        
        # 스타일 적용
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='크롤링 결과')
            
            # 스타일링
            workbook = writer.book
            worksheet = writer.sheets['크롤링 결과']
            
            # 헤더 스타일
            from openpyxl.styles import PatternFill, Font, Alignment
            header_fill = PatternFill(start_color='{request.get('brand_color', '366092').replace('#', '')}', 
                                     end_color='{request.get('brand_color', '366092').replace('#', '')}', 
                                     fill_type='solid')
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
        
        return filename

# 특수 기능 추가
{self._generate_special_features(request)}
'''
        
        # 파일 저장
        crawler_file = os.path.join(project_dir, f"{request.get('class_name', 'custom_crawler')}.py")
        with open(crawler_file, 'w', encoding='utf-8') as f:
            f.write(crawler_code)
    
    def _generate_special_features(self, request: Dict) -> str:
        """고객 요청 특수 기능 생성"""
        features = []
        
        # 로그인 기능
        if request.get('needs_login', False):
            features.append('''
def login(self, username, password, login_url):
    """로그인 기능"""
    session = requests.Session()
    login_data = {
        'username': username,
        'password': password
    }
    session.post(login_url, data=login_data)
    return session
''')
        
        # 페이지네이션
        if request.get('needs_pagination', False):
            features.append('''
def crawl_multiple_pages(self, base_url, max_pages=10):
    """여러 페이지 크롤링"""
    for page in range(1, max_pages + 1):
        url = f"{base_url}?page={page}"
        self.crawl(url)
        time.sleep(self.delay)
''')
        
        # API 호출
        if request.get('needs_api', False):
            features.append('''
def call_api(self, api_url, params=None):
    """API 호출"""
    response = requests.get(api_url, params=params)
    return response.json()
''')
        
        # 이미지 다운로드
        if request.get('needs_image_download', False):
            features.append('''
def download_images(self, img_urls, save_dir="images"):
    """이미지 다운로드"""
    os.makedirs(save_dir, exist_ok=True)
    for i, url in enumerate(img_urls):
        response = requests.get(url)
        filename = os.path.join(save_dir, f"image_{i}.jpg")
        with open(filename, 'wb') as f:
            f.write(response.content)
''')
        
        return '\n'.join(features)
    
    def _generate_gui(self, project_dir: str, request: Dict):
        """GUI 인터페이스 생성"""
        
        gui_code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{request.get('project_name', 'Custom Crawler')} GUI
{request.get('company_name', '고객사')} 전용 인터페이스
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
from {request.get('class_name', 'custom_crawler')} import {request.get('class_name', 'CustomCrawler')}
import os
from datetime import datetime

class CrawlerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("{request.get('project_name', 'Custom Crawler')} v{request.get('version', '1.0.0')}")
        self.root.geometry("{request.get('window_size', '900x700')}")
        
        # 브랜드 색상
        self.brand_color = "{request.get('brand_color', '#2196F3')}"
        
        # 크롤러 인스턴스
        self.crawler = {request.get('class_name', 'CustomCrawler')}()
        
        self.create_widgets()
        
    def create_widgets(self):
        """UI 생성"""
        # 헤더
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=10, pady=5)
        
        title = ttk.Label(header, text="{request.get('project_name', 'Custom Crawler')}", 
                         font=('맑은 고딕', 16, 'bold'))
        title.pack(side=tk.LEFT)
        
        # URL 입력
        input_frame = ttk.LabelFrame(self.root, text="크롤링 설정", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(input_frame, text="URL:").grid(row=0, column=0, sticky=tk.W)
        self.url_entry = ttk.Entry(input_frame, width=60)
        self.url_entry.grid(row=0, column=1, padx=5)
        self.url_entry.insert(0, "{request.get('default_url', '')}")
        
        # 프리셋 버튼들
        preset_frame = ttk.Frame(input_frame)
        preset_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        {self._generate_preset_buttons(request)}
        
        # 선택자 입력
        selector_frame = ttk.LabelFrame(self.root, text="데이터 필드", padding=10)
        selector_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.selector_text = scrolledtext.ScrolledText(selector_frame, height=8)
        self.selector_text.pack(fill=tk.BOTH, expand=True)
        
        # 기본 선택자
        default_selectors = """# {request.get('company_name', '고객사')} 맞춤 선택자
{self._generate_default_selectors(request)}"""
        self.selector_text.insert(1.0, default_selectors)
        
        # 컨트롤 버튼
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10)
        
        self.start_btn = ttk.Button(control_frame, text="🚀 크롤링 시작", 
                                   command=self.start_crawling)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_csv_btn = ttk.Button(control_frame, text="💾 CSV 저장", 
                                      command=self.save_csv)
        self.save_csv_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_excel_btn = ttk.Button(control_frame, text="📊 Excel 저장", 
                                        command=self.save_excel)
        self.save_excel_btn.pack(side=tk.LEFT, padx=5)
        
        # 로그
        log_frame = ttk.LabelFrame(self.root, text="실행 로그", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 상태바
        self.status_bar = ttk.Label(self.root, text="준비 완료", relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X)
    
    def start_crawling(self):
        """크롤링 시작"""
        url = self.url_entry.get()
        if not url:
            messagebox.showwarning("경고", "URL을 입력하세요.")
            return
        
        # 선택자 파싱
        selectors = {{}}
        for line in self.selector_text.get(1.0, tk.END).split('\\n'):
            if ':' in line and not line.startswith('#'):
                key, value = line.split(':', 1)
                selectors[key.strip()] = value.strip()
        
        # 크롤링 실행
        self.log("크롤링 시작: " + url)
        result = self.crawler.crawl(url, selectors)
        
        if result:
            self.log(f"✅ 성공: {{len(result)}} 필드 수집")
            self.status_bar.config(text=f"크롤링 완료 - {{len(self.crawler.results)}} 항목")
        else:
            self.log("❌ 크롤링 실패")
    
    def save_csv(self):
        """CSV 저장"""
        if not self.crawler.results:
            messagebox.showwarning("경고", "저장할 데이터가 없습니다.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV 파일", "*.csv")],
            initialfile=f"{{self.crawler.name}}_{{datetime.now().strftime('%Y%m%d')}}.csv"
        )
        
        if filename:
            self.crawler.save_to_csv(filename)
            self.log(f"💾 CSV 저장 완료: {{filename}}")
            messagebox.showinfo("성공", "CSV 파일이 저장되었습니다.")
    
    def save_excel(self):
        """Excel 저장"""
        if not self.crawler.results:
            messagebox.showwarning("경고", "저장할 데이터가 없습니다.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel 파일", "*.xlsx")],
            initialfile=f"{{self.crawler.name}}_{{datetime.now().strftime('%Y%m%d')}}.xlsx"
        )
        
        if filename:
            self.crawler.save_to_excel(filename)
            self.log(f"📊 Excel 저장 완료: {{filename}}")
            messagebox.showinfo("성공", "Excel 파일이 저장되었습니다.")
    
    def log(self, message):
        """로그 출력"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"[{{timestamp}}] {{message}}\\n")
        self.log_text.see(tk.END)
    
    {self._generate_preset_methods(request)}

def main():
    root = tk.Tk()
    app = CrawlerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
'''
        
        # GUI 파일 저장
        gui_file = os.path.join(project_dir, "gui.py")
        with open(gui_file, 'w', encoding='utf-8') as f:
            f.write(gui_code)
    
    def _generate_preset_buttons(self, request: Dict) -> str:
        """프리셋 버튼 생성"""
        buttons = []
        for i, preset in enumerate(request.get('presets', [])):
            buttons.append(f'''
        ttk.Button(preset_frame, text="{preset['name']}", 
                  command=self.preset_{i}).pack(side=tk.LEFT, padx=2)''')
        return ''.join(buttons)
    
    def _generate_preset_methods(self, request: Dict) -> str:
        """프리셋 메서드 생성"""
        methods = []
        for i, preset in enumerate(request.get('presets', [])):
            methods.append(f'''
    def preset_{i}(self):
        """프리셋: {preset['name']}"""
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, "{preset.get('url', '')}")
        self.selector_text.delete(1.0, tk.END)
        selectors = """{preset.get('selectors', '')}"""
        self.selector_text.insert(1.0, selectors)
        self.log("프리셋 적용: {preset['name']}")
''')
        return ''.join(methods)
    
    def _generate_default_selectors(self, request: Dict) -> str:
        """기본 선택자 생성"""
        selectors = []
        for field, selector in request.get('data_fields', {}).items():
            selectors.append(f"{field}: {selector}")
        return '\n'.join(selectors)
    
    def _generate_presets(self, project_dir: str, request: Dict):
        """프리셋 설정 파일 생성"""
        presets = {
            "version": request.get('version', '1.0.0'),
            "presets": request.get('presets', []),
            "default_settings": {
                "delay": request.get('delay', 0.5),
                "max_pages": request.get('max_pages', 10),
                "timeout": request.get('timeout', 30)
            }
        }
        
        preset_file = os.path.join(project_dir, "presets.json")
        with open(preset_file, 'w', encoding='utf-8') as f:
            json.dump(presets, f, ensure_ascii=False, indent=2)
    
    def _generate_build_scripts(self, project_dir: str, request: Dict):
        """빌드 스크립트 생성"""
        
        # requirements.txt
        requirements = f"""# {request.get('project_name', 'Custom Crawler')} Dependencies
requests==2.31.0
beautifulsoup4==4.12.2
pandas==2.2.3
openpyxl==3.1.2
lxml==5.1.0
pyinstaller==6.3.0
"""
        if request.get('needs_selenium', False):
            requirements += "selenium==4.16.0\nwebdriver-manager==4.0.1\n"
        
        req_file = os.path.join(project_dir, "requirements.txt")
        with open(req_file, 'w', encoding='utf-8') as f:
            f.write(requirements)
        
        # build.py
        build_script = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""빌드 스크립트 - {request.get('project_name', 'Custom Crawler')}"""

import PyInstaller.__main__
import os
import shutil

def build():
    """EXE 빌드"""
    # 이전 빌드 정리
    for dir in ['build', 'dist', '__pycache__']:
        if os.path.exists(dir):
            shutil.rmtree(dir)
    
    # PyInstaller 실행
    PyInstaller.__main__.run([
        'gui.py',
        '--name', '{request.get('exe_name', 'CustomCrawler')}',
        '--onefile',
        '--windowed',
        '--icon', 'icon.ico',
        '--add-data', 'presets.json;.',
        '--hidden-import', 'tkinter',
        '--hidden-import', 'requests',
        '--hidden-import', 'bs4',
        '--hidden-import', 'pandas',
        '--hidden-import', 'openpyxl',
        '--clean',
        '--noconfirm'
    ])
    
    print("✅ 빌드 완료!")
    print(f"실행 파일: dist/{request.get('exe_name', 'CustomCrawler')}.exe")

if __name__ == "__main__":
    build()
'''
        
        build_file = os.path.join(project_dir, "build.py")
        with open(build_file, 'w', encoding='utf-8') as f:
            f.write(build_script)
        
        # build.bat
        batch_script = f"""@echo off
echo ========================================
echo {request.get('project_name', 'Custom Crawler')} 빌드
echo ========================================
echo.

REM 가상환경 생성
if not exist "venv" (
    python -m venv venv
)

REM 가상환경 활성화
call venv\\Scripts\\activate.bat

REM 의존성 설치
pip install -r requirements.txt

REM 빌드 실행
python build.py

echo.
echo 빌드 완료!
pause
"""
        
        batch_file = os.path.join(project_dir, "build.bat")
        with open(batch_file, 'w', encoding='utf-8') as f:
            f.write(batch_script)
    
    def _generate_installer(self, project_dir: str, request: Dict):
        """Inno Setup 인스톨러 스크립트 생성"""
        
        installer_script = f'''; Inno Setup Script for {request.get('project_name', 'Custom Crawler')}

#define MyAppName "{request.get('project_name', 'Custom Crawler')}"
#define MyAppVersion "{request.get('version', '1.0.0')}"
#define MyAppPublisher "{request.get('company_name', '고객사')}"
#define MyAppExeName "{request.get('exe_name', 'CustomCrawler')}.exe"

[Setup]
AppId={{{{request.get('app_id', 'E8F4B3C2-9A7D-4F2E-B5C8-1D3A6E9F8B2C')}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
DefaultDirName={{autopf}}\\{{#MyAppName}}
DefaultGroupName={{#MyAppName}}
OutputDir=installer
OutputBaseFilename={{#MyAppName}}_Setup_v{{#MyAppVersion}}
SetupIconFile=icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"

[Files]
Source: "dist\\{{#MyAppExeName}}"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{group}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange(MyAppName, '&', '&&')}}}}"; Flags: nowait postinstall skipifsilent
'''
        
        installer_file = os.path.join(project_dir, "installer.iss")
        with open(installer_file, 'w', encoding='utf-8') as f:
            f.write(installer_script)
    
    def _generate_documentation(self, project_dir: str, request: Dict):
        """사용 설명서 생성"""
        
        readme = f"""# {request.get('project_name', 'Custom Crawler')}

## 소개
{request.get('company_name', '고객사')} 전용 크롤링 툴
{request.get('description', '웹 데이터 자동 수집 도구')}

## 버전
v{request.get('version', '1.0.0')}

## 주요 기능
{self._generate_feature_list(request)}

## 사용법

### 1. 프로그램 실행
- 바탕화면의 "{request.get('project_name', 'Custom Crawler')}" 아이콘 더블클릭
- 또는 시작 메뉴에서 실행

### 2. URL 입력
- 크롤링할 웹사이트 주소 입력
{f"- 기본 URL: {request.get('default_url', '')}" if request.get('default_url') else ""}

### 3. 데이터 필드 설정
- 프리셋 버튼 클릭 또는 직접 입력
- 형식: 필드명: CSS선택자

### 4. 크롤링 실행
- [🚀 크롤링 시작] 버튼 클릭
- 실시간 로그 확인

### 5. 결과 저장
- [💾 CSV 저장] - CSV 형식으로 저장
- [📊 Excel 저장] - Excel 형식으로 저장 (권장)

## 프리셋 목록
{self._generate_preset_docs(request)}

## 지원 사이트
{chr(10).join(['- ' + site for site in request.get('target_sites', [])])}

## 문의처
- 담당자: {request.get('contact_name', '담당자')}
- 이메일: {request.get('contact_email', 'support@example.com')}
- 전화: {request.get('contact_phone', '02-1234-5678')}

## 라이센스
{request.get('license', '© 2024 All rights reserved.')}
"""
        
        readme_file = os.path.join(project_dir, "README.md")
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme)
    
    def _generate_feature_list(self, request: Dict) -> str:
        """기능 목록 생성"""
        features = ["- ✅ 실시간 웹 크롤링", "- 📊 CSV/Excel 저장", "- 🎯 맞춤형 프리셋"]
        
        if request.get('needs_login'):
            features.append("- 🔐 로그인 지원")
        if request.get('needs_pagination'):
            features.append("- 📄 페이지네이션")
        if request.get('needs_api'):
            features.append("- 🔌 API 연동")
        if request.get('needs_image_download'):
            features.append("- 🖼️ 이미지 다운로드")
        if request.get('needs_selenium'):
            features.append("- 🌐 동적 페이지 지원")
        
        return '\n'.join(features)
    
    def _generate_preset_docs(self, request: Dict) -> str:
        """프리셋 문서 생성"""
        docs = []
        for preset in request.get('presets', []):
            docs.append(f"### {preset['name']}")
            docs.append(f"- URL: {preset.get('url', '')}")
            docs.append(f"- 용도: {preset.get('description', '')}")
            docs.append("")
        return '\n'.join(docs)
    
    def _generate_resources(self, project_dir: str, request: Dict):
        """리소스 파일 생성"""
        
        # 아이콘 (임시)
        icon_file = os.path.join(project_dir, "icon.ico")
        with open(icon_file, 'w', encoding='utf-8') as f:
            f.write(request.get('icon_emoji', '🕷️'))
        
        # 설정 파일
        config = {
            "app_name": request.get('project_name', 'Custom Crawler'),
            "version": request.get('version', '1.0.0'),
            "company": request.get('company_name', '고객사'),
            "settings": {
                "default_delay": request.get('delay', 0.5),
                "max_pages": request.get('max_pages', 10),
                "timeout": request.get('timeout', 30),
                "user_agent": request.get('user_agent', 'Mozilla/5.0')
            }
        }
        
        config_file = os.path.join(project_dir, "config.json")
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)


# 사용 예시
def create_crawler_from_request(customer_request: Dict):
    """고객 요청사항으로 크롤러 생성"""
    
    factory = CrawlerFactory()
    project_path = factory.create_custom_crawler(customer_request)
    
    print(f"""
    ✨ 크롤러 생성 완료!
    ===========================
    프로젝트 경로: {project_path}
    
    다음 단계:
    1. cd {project_path}
    2. build.bat 실행 (Windows)
    3. installer/ 폴더에서 설치 파일 확인
    
    생성된 파일:
    - gui.py: 메인 GUI 애플리케이션
    - {customer_request.get('class_name', 'custom_crawler')}.py: 크롤러 엔진
    - build.bat: 빌드 스크립트
    - installer.iss: 인스톨러 스크립트
    - README.md: 사용 설명서
    """)
    
    return project_path


if __name__ == "__main__":
    # 테스트용 고객 요청사항
    sample_request = {
        "project_name": "네이버 뉴스 크롤러",
        "company_name": "ABC 기업",
        "version": "1.0.0",
        "description": "네이버 뉴스 자동 수집 도구",
        "exe_name": "NaverNewsCrawler",
        "class_name": "NaverCrawler",
        "window_size": "900x700",
        "brand_color": "#03C75A",  # 네이버 그린
        
        "target_sites": [
            "https://news.naver.com",
            "https://news.naver.com/section/105"
        ],
        
        "default_url": "https://news.naver.com/section/105",
        
        "data_fields": {
            "title": ".sa_text_title",
            "content": ".sa_text_lede", 
            "date": ".sa_text_datetime",
            "author": ".sa_text_press",
            "link": ".sa_text a[href]"
        },
        
        "presets": [
            {
                "name": "IT 뉴스",
                "url": "https://news.naver.com/section/105",
                "description": "IT/과학 뉴스",
                "selectors": "title: .sa_text_title\\ncontent: .sa_text_lede\\ndate: .sa_text_datetime"
            },
            {
                "name": "경제 뉴스",
                "url": "https://news.naver.com/section/101",
                "description": "경제 뉴스",
                "selectors": "title: .sa_text_title\\ncontent: .sa_text_lede\\ndate: .sa_text_datetime"
            }
        ],
        
        "needs_pagination": True,
        "needs_image_download": False,
        "needs_login": False,
        "needs_api": False,
        "needs_selenium": False,
        
        "delay": 0.5,
        "max_pages": 10,
        "timeout": 30,
        
        "contact_name": "홍길동",
        "contact_email": "support@abc.com",
        "contact_phone": "02-1234-5678",
        
        "license": "© 2024 ABC 기업. All rights reserved.",
        "icon_emoji": "📰"
    }
    
    # 크롤러 생성
    create_crawler_from_request(sample_request)