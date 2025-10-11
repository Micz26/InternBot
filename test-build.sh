#!/bin/bash

echo "🧪 Testing Docker Build for InternBot"
echo "====================================="

# Test frontend build
echo "📦 Testing frontend build..."
cd frontend
docker build -t internbot-frontend-test .
if [ $? -eq 0 ]; then
    echo "✅ Frontend build successful!"
else
    echo "❌ Frontend build failed!"
    exit 1
fi

# Test backend build
echo "📦 Testing backend build..."
cd ../backend
docker build -t internbot-backend-test .
if [ $? -eq 0 ]; then
    echo "✅ Backend build successful!"
else
    echo "❌ Backend build failed!"
    exit 1
fi

echo ""
echo "🎉 All builds successful! You can now run:"
echo "   docker-compose up --build"
