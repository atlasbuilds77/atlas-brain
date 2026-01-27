#!/bin/bash

# Kronos Core Engine Startup Script
# Usage: ./start.sh [dev|prod]

set -e

ENV=${1:-dev}

echo "🚀 Starting Kronos Core Engine in $ENV mode..."

case $ENV in
    dev)
        echo "📦 Installing dependencies..."
        pip install -r requirements.txt
        
        echo "🔧 Setting up database..."
        # Create initial migration if needed
        if [ ! -d "alembic/versions" ]; then
            echo "📝 Creating initial database migration..."
            alembic revision --autogenerate -m "Initial migration"
        fi
        
        echo "🔄 Running database migrations..."
        alembic upgrade head
        
        echo "⚡ Starting development server..."
        uvicorn main:app --host 0.0.0.0 --port 8000 --reload
        ;;
        
    prod)
        echo "🐳 Starting with Docker Compose..."
        docker-compose up -d
        
        echo "📊 Services started:"
        echo "  - API: http://localhost:8000"
        echo "  - API Docs: http://localhost:8000/docs"
        echo "  - Flower (Celery monitor): http://localhost:5555"
        echo "  - PostgreSQL: localhost:5432"
        echo "  - Redis: localhost:6379"
        
        echo ""
        echo "📋 To view logs:"
        echo "  docker-compose logs -f api"
        echo "  docker-compose logs -f worker"
        ;;
        
    *)
        echo "❌ Unknown environment: $ENV"
        echo "Usage: ./start.sh [dev|prod]"
        exit 1
        ;;
esac