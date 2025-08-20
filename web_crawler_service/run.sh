#!/bin/bash

echo "🕷️  크롤링 마스터 서버 시작 스크립트"
echo "========================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Python 버전 확인
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD=python3
    elif command -v python &> /dev/null; then
        PYTHON_CMD=python
    else
        echo -e "${RED}❌ Python이 설치되지 않았습니다.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Python 발견: $($PYTHON_CMD --version)${NC}"
}

# 가상환경 설정
setup_venv() {
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}📦 가상환경 생성 중...${NC}"
        $PYTHON_CMD -m venv venv
    fi
    
    echo -e "${GREEN}✅ 가상환경 활성화${NC}"
    source venv/bin/activate
}

# 의존성 설치
install_deps() {
    echo -e "${YELLOW}📦 의존성 설치 중...${NC}"
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt
}

# 디렉토리 생성
create_dirs() {
    echo -e "${YELLOW}📁 필요한 디렉토리 생성 중...${NC}"
    mkdir -p templates downloads
}

# 서버 실행
run_server() {
    echo -e "${GREEN}🚀 서버 시작!${NC}"
    echo "========================================="
    echo -e "${GREEN}📍 주소: http://localhost:8000${NC}"
    echo -e "${GREEN}📊 엑셀 파일은 downloads 폴더에 저장됩니다${NC}"
    echo "========================================="
    echo ""
    
    # 서버 실행
    uvicorn simple_main:app --host 0.0.0.0 --port 8000 --reload
}

# 메인 실행 플로우
main() {
    echo ""
    check_python
    setup_venv
    install_deps
    create_dirs
    run_server
}

# 스크립트 실행
main