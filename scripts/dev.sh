#!/bin/bash

# Development script for InternBot
# This script helps you start the development environment

echo "🚀 Starting InternBot Development Environment"
echo "=============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it first."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Ask user what they want to do
echo "What would you like to do?"
echo "1) Start full development environment (backend + frontend + database)"
echo "2) Start only backend and database"
echo "3) Start only frontend (requires backend to be running)"
echo "4) Stop all services"
echo "5) View logs"
echo "6) Clean up (remove containers and volumes)"
echo ""
read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo "🔄 Starting full development environment..."
        docker-compose -f docker-compose.dev.yml up --build
        ;;
    2)
        echo "🔄 Starting backend and database..."
        docker-compose -f docker-compose.dev.yml up --build db backend
        ;;
    3)
        echo "🔄 Starting frontend only..."
        echo "⚠️  Make sure backend is running on port 8000"
        cd frontend && npm install && npm run dev
        ;;
    4)
        echo "🛑 Stopping all services..."
        docker-compose -f docker-compose.dev.yml down
        ;;
    5)
        echo "📋 Viewing logs..."
        docker-compose -f docker-compose.dev.yml logs -f
        ;;
    6)
        echo "🧹 Cleaning up..."
        docker-compose -f docker-compose.dev.yml down -v --remove-orphans
        docker system prune -f
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "✅ Done!"
