#!/bin/bash

# PrepGenie Deployment Setup Script
# This script automates local deployment with Docker

set -e

echo "🚀 PrepGenie Deployment Setup"
echo "=============================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Edit .env with your credentials:"
    echo "   - SUPABASE_URL"
    echo "   - SUPABASE_SERVICE_ROLE_KEY"
    echo "   - GEMINI_API_KEY"
    echo "   - REACT_APP_SUPABASE_URL"
    echo "   - REACT_APP_SUPABASE_ANON_KEY"
    echo ""
    echo "Press Enter when ready to continue..."
    read
fi

# Load environment variables
export $(cat .env | grep -v '#' | xargs)

echo "🔧 Building Docker images..."
docker-compose build

echo ""
echo "📦 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "🌐 Access URLs:"
    echo "   Frontend:  http://localhost"
    echo "   Backend:   http://localhost:8000"
    echo "   Health:    http://localhost:8000/health"
    echo ""
    echo "📚 Useful commands:"
    echo "   View logs:     docker-compose logs -f"
    echo "   Stop services: docker-compose down"
    echo "   Bash in backend: docker-compose exec backend bash"
    echo ""
else
    echo "❌ Services failed to start. Check logs:"
    docker-compose logs
    exit 1
fi

echo "✨ Setup complete!"
