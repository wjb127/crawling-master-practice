#!/bin/bash

echo "🚀 Fly.io 배포 스크립트"
echo "========================"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fly CLI 설치 확인
check_fly_cli() {
    if ! command -v flyctl &> /dev/null; then
        echo -e "${YELLOW}📦 Fly CLI가 설치되지 않았습니다. 설치 중...${NC}"
        
        # OS별 설치
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            brew install flyctl
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            curl -L https://fly.io/install.sh | sh
            export PATH="$HOME/.fly/bin:$PATH"
        else
            echo -e "${RED}❌ 지원하지 않는 OS입니다. https://fly.io/docs/hands-on/install-flyctl/ 에서 수동 설치해주세요.${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✅ Fly CLI 확인됨${NC}"
}

# Fly.io 로그인
login_fly() {
    echo -e "${BLUE}🔐 Fly.io 로그인...${NC}"
    
    if ! flyctl auth whoami &> /dev/null; then
        flyctl auth login
    else
        echo -e "${GREEN}✅ 이미 로그인되어 있습니다${NC}"
    fi
}

# 앱 생성 또는 확인
setup_app() {
    APP_NAME="crawling-master-kr"
    
    echo -e "${BLUE}🏗️  앱 설정 중: ${APP_NAME}${NC}"
    
    # 앱이 이미 존재하는지 확인
    if flyctl apps list | grep -q "$APP_NAME"; then
        echo -e "${GREEN}✅ 앱이 이미 존재합니다${NC}"
    else
        echo -e "${YELLOW}📱 새 앱 생성 중...${NC}"
        flyctl apps create "$APP_NAME" --region nrt
    fi
}

# 볼륨 생성
create_volume() {
    echo -e "${BLUE}💾 데이터 볼륨 확인...${NC}"
    
    if ! flyctl volumes list --app crawling-master-kr | grep -q "crawling_data"; then
        echo -e "${YELLOW}📂 볼륨 생성 중...${NC}"
        flyctl volumes create crawling_data --app crawling-master-kr --region nrt --size 1
    else
        echo -e "${GREEN}✅ 볼륨이 이미 존재합니다${NC}"
    fi
}

# 시크릿 설정
set_secrets() {
    echo -e "${BLUE}🔑 환경 변수 설정...${NC}"
    
    # 프로덕션 환경 변수 설정
    flyctl secrets set \
        ENVIRONMENT=production \
        MAX_CONCURRENT_JOBS=20 \
        MAX_PAGES_PER_JOB=50 \
        RATE_LIMIT_DELAY=0.5 \
        --app crawling-master-kr
    
    echo -e "${GREEN}✅ 시크릿 설정 완료${NC}"
}

# 배포
deploy() {
    echo -e "${BLUE}🚀 배포 시작...${NC}"
    
    # 프로덕션 파일 복사
    cp simple_main_prod.py simple_main.py
    
    # Dockerfile 선택
    if [ -f "Dockerfile.fly" ]; then
        export DOCKERFILE="Dockerfile.fly"
    fi
    
    # 배포 실행
    flyctl deploy --app crawling-master-kr
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✨ 배포 성공!${NC}"
        echo -e "${GREEN}🌐 URL: https://crawling-master-kr.fly.dev${NC}"
        
        # 앱 정보 표시
        flyctl info --app crawling-master-kr
        
        # 로그 확인 옵션
        echo ""
        echo -e "${YELLOW}로그를 확인하려면: flyctl logs --app crawling-master-kr${NC}"
        echo -e "${YELLOW}앱을 열려면: flyctl open --app crawling-master-kr${NC}"
    else
        echo -e "${RED}❌ 배포 실패!${NC}"
        echo -e "${YELLOW}로그 확인: flyctl logs --app crawling-master-kr${NC}"
        exit 1
    fi
}

# 상태 확인
check_status() {
    echo ""
    echo -e "${BLUE}📊 앱 상태 확인...${NC}"
    flyctl status --app crawling-master-kr
}

# 메인 실행 플로우
main() {
    echo ""
    echo -e "${BLUE}크롤링 마스터 서비스를 Fly.io에 배포합니다${NC}"
    echo "========================================="
    echo ""
    
    check_fly_cli
    login_fly
    setup_app
    create_volume
    set_secrets
    deploy
    check_status
    
    echo ""
    echo -e "${GREEN}🎉 모든 작업이 완료되었습니다!${NC}"
    echo -e "${GREEN}🌐 서비스 URL: https://crawling-master-kr.fly.dev${NC}"
    echo ""
}

# 스크립트 실행
main