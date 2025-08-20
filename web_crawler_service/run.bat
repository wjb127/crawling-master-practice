@echo off
echo =====================================
echo 🕷️  크롤링 마스터 서버 시작
echo =====================================
echo.

REM Python 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았습니다.
    echo Python을 먼저 설치해주세요: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python 발견
echo.

REM 가상환경 확인 및 생성
if not exist "venv" (
    echo 📦 가상환경 생성 중...
    python -m venv venv
)

REM 가상환경 활성화
echo ✅ 가상환경 활성화
call venv\Scripts\activate.bat

REM 의존성 설치
echo 📦 의존성 설치 중...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

REM 디렉토리 생성
echo 📁 필요한 디렉토리 생성 중...
if not exist "templates" mkdir templates
if not exist "downloads" mkdir downloads

REM 서버 시작
echo.
echo =====================================
echo 🚀 서버 시작!
echo =====================================
echo 📍 주소: http://localhost:8000
echo 📊 엑셀 파일은 downloads 폴더에 저장됩니다
echo =====================================
echo.

uvicorn simple_main:app --host 0.0.0.0 --port 8000 --reload

pause