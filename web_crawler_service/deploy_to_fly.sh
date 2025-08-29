#!/bin/bash

echo "🚀 Fly.io 배포 시작..."

# 1. web_crawler_service 디렉토리로 이동
cd web_crawler_service

# 2. Fly 앱 생성 또는 기존 앱 사용
echo "📦 Fly 앱 설정 중..."
if ! fly status 2>/dev/null; then
    echo "새 앱을 생성합니다..."
    fly launch --name crawling-master-kr --region nrt --no-deploy
else
    echo "기존 앱을 사용합니다..."
fi

# 3. 배포
echo "🚢 배포 시작..."
fly deploy

# 4. 배포 확인
echo "✅ 배포 상태 확인..."
fly status
fly open

echo "🎉 배포 완료! 앱 URL: https://crawling-master-kr.fly.dev"