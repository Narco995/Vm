#!/bin/bash
set -e

echo "🤖 Deploying Advanced Telegram AI Bot..."

cd "$(dirname "$0")/.."

if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env with your API keys."
    exit 1
fi

echo "📦 Building Docker image..."
docker-compose -f deploy/docker-compose.yml build --no-cache

echo "🚀 Starting bot..."
docker-compose -f deploy/docker-compose.yml up -d

echo "✅ Bot deployed successfully!"
echo ""
echo "📊 View logs:  docker-compose -f deploy/docker-compose.yml logs -f"
echo "🛑 Stop bot:   docker-compose -f deploy/docker-compose.yml down"
echo "🔄 Restart:    docker-compose -f deploy/docker-compose.yml restart"
