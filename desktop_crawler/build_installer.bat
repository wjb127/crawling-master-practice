@echo off
echo =========================================
echo 크롤링 마스터 인스톨러 빌드 스크립트
echo =========================================
echo.

REM Python 환경 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python이 설치되지 않았습니다.
    pause
    exit /b 1
)

echo [1/5] 가상환경 생성 및 활성화...
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat

echo [2/5] 의존성 설치...
pip install --upgrade pip >nul 2>&1
pip install -r requirements_desktop.txt

echo [3/5] PyInstaller로 EXE 빌드...
python build_exe.py

if not exist "dist\CrawlingMaster.exe" (
    echo [ERROR] EXE 빌드 실패!
    pause
    exit /b 1
)

echo [4/5] Inno Setup 컴파일...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_script.iss
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    "C:\Program Files\Inno Setup 6\ISCC.exe" installer_script.iss
) else (
    echo [WARNING] Inno Setup이 설치되지 않았습니다.
    echo 다운로드: https://jrsoftware.org/isdl.php
    echo EXE 파일만 생성되었습니다: dist\CrawlingMaster.exe
)

echo [5/5] 배포 패키지 생성...
if not exist "release" mkdir release

REM ZIP 파일 생성 (PowerShell 사용)
powershell -Command "Compress-Archive -Path 'dist\CrawlingMaster.exe', 'README_USER.md' -DestinationPath 'release\CrawlingMaster_v1.0.0_Portable.zip' -Force"

echo.
echo =========================================
echo 빌드 완료!
echo =========================================
echo.
echo 생성된 파일:
echo - EXE: dist\CrawlingMaster.exe
if exist "installer\CrawlingMaster_Setup_v1.0.0.exe" (
    echo - 인스톨러: installer\CrawlingMaster_Setup_v1.0.0.exe
)
echo - 포터블: release\CrawlingMaster_v1.0.0_Portable.zip
echo.
echo 배포 준비 완료!
echo.
pause