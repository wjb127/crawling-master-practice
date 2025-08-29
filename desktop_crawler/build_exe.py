#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyInstaller를 사용한 EXE 빌드 스크립트
"""

import PyInstaller.__main__
import os
import shutil
from datetime import datetime

# 빌드 설정
APP_NAME = "CrawlingMaster"
APP_VERSION = "1.0.0"
AUTHOR = "크몽 프리랜서"
DESCRIPTION = "실시간 웹 크롤링 및 CSV 내보내기 툴"

def clean_build():
    """빌드 폴더 정리"""
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = [f'{APP_NAME}.spec']
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"삭제됨: {dir_name}")
    
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"삭제됨: {file_name}")

def build_exe():
    """EXE 빌드"""
    print(f"\n{'='*50}")
    print(f"{APP_NAME} v{APP_VERSION} 빌드 시작")
    print(f"{'='*50}\n")
    
    # PyInstaller 옵션
    options = [
        'crawler_gui.py',                    # 메인 스크립트
        '--name', APP_NAME,                  # 실행 파일 이름
        '--onefile',                          # 단일 파일로 생성
        '--windowed',                         # 콘솔 창 숨기기 (GUI 앱)
        '--icon', 'icon.ico',                # 아이콘 (있는 경우)
        '--add-data', 'icon.ico;.',          # 아이콘 포함
        '--hidden-import', 'tkinter',
        '--hidden-import', 'requests',
        '--hidden-import', 'bs4',
        '--hidden-import', 'pandas',
        '--hidden-import', 'openpyxl',
        '--clean',                            # 빌드 전 캐시 정리
        '--noconfirm',                        # 덮어쓰기 확인 없음
        
        # 최적화 옵션
        '--optimize', '2',                    # 최적화 레벨
        
        # 버전 정보
        '--version-file', 'version_info.txt'  # 버전 정보 파일 (있는 경우)
    ]
    
    # 아이콘 파일이 없으면 옵션에서 제거
    if not os.path.exists('icon.ico'):
        options.remove('--icon')
        options.remove('icon.ico')
        options.remove('--add-data')
        options.remove('icon.ico;.')
    
    # 버전 정보 파일이 없으면 옵션에서 제거
    if not os.path.exists('version_info.txt'):
        options.remove('--version-file')
        options.remove('version_info.txt')
    
    # 빌드 실행
    try:
        PyInstaller.__main__.run(options)
        print(f"\n✅ 빌드 성공!")
        print(f"실행 파일 위치: dist/{APP_NAME}.exe")
        
        # 실행 파일 크기 확인
        exe_path = f"dist/{APP_NAME}.exe"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"파일 크기: {size_mb:.2f} MB")
        
        return True
    except Exception as e:
        print(f"\n❌ 빌드 실패: {str(e)}")
        return False

def create_portable_package():
    """포터블 패키지 생성"""
    print(f"\n포터블 패키지 생성 중...")
    
    # 패키지 폴더 생성
    package_name = f"{APP_NAME}_v{APP_VERSION}_Portable"
    package_dir = f"dist/{package_name}"
    
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    # 필요한 파일 복사
    files_to_copy = [
        (f"dist/{APP_NAME}.exe", f"{package_dir}/{APP_NAME}.exe"),
        ("README_USER.md", f"{package_dir}/사용설명서.txt"),
    ]
    
    for src, dst in files_to_copy:
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"복사됨: {src} -> {dst}")
    
    # 폴더 구조 생성
    os.makedirs(f"{package_dir}/results", exist_ok=True)
    os.makedirs(f"{package_dir}/logs", exist_ok=True)
    
    # 배치 파일 생성 (빠른 실행용)
    batch_content = f"""@echo off
title {APP_NAME} v{APP_VERSION}
start {APP_NAME}.exe
exit"""
    
    with open(f"{package_dir}/크롤링마스터_실행.bat", 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    print(f"✅ 포터블 패키지 생성 완료: {package_dir}")
    return package_dir

def main():
    """메인 빌드 프로세스"""
    # 1. 이전 빌드 정리
    clean_build()
    
    # 2. EXE 빌드
    if build_exe():
        # 3. 포터블 패키지 생성
        package_dir = create_portable_package()
        
        print(f"\n{'='*50}")
        print(f"빌드 완료!")
        print(f"{'='*50}")
        print(f"\n다음 단계:")
        print(f"1. {package_dir} 폴더를 압축하여 배포")
        print(f"2. 또는 Inno Setup으로 인스톨러 생성")
        print(f"3. 실행: dist/{APP_NAME}.exe")

if __name__ == "__main__":
    main()