#!/bin/bash

echo "🚀 InternBot Setup Script"
echo "========================"

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating backend/.env file..."
    cat > backend/.env << EOF
# OpenAI API Configuration
# Replace with your actual OpenAI API key from https://platform.openai.com/account/api-keys
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# Database Configuration
DB_HOST=db
DB_PORT=5432
DB_NAME=internbot
DB_USER=postgres
DB_PASSWORD=password

# Optional: Table name
OFFERS_TABLE_NAME=offers
EOF
    echo "✅ Created backend/.env file"
    echo ""
    echo "⚠️  IMPORTANT: You need to edit backend/.env and add your actual OpenAI API key!"
    echo "   Get your API key from: https://platform.openai.com/account/api-keys"
    echo ""
else
    echo "✅ backend/.env file already exists"
fi

# Load server configuration from config.env if it exists
if [ -f "config.env" ]; then
    echo "📋 Loading server configuration from config.env..."
    source config.env
    echo "✅ Loaded configuration: SERVER_IP=${SERVER_IP:-localhost}"
else
    echo "⚠️  config.env not found, using default server IP: localhost"
    SERVER_IP="localhost"
    VITE_BACKEND_URL="http://localhost:8000"
fi

# Check if frontend .env.local exists
if [ ! -f "frontend/.env.local" ]; then
    echo "📝 Creating frontend/.env.local file..."
    cat > frontend/.env.local << EOF
VITE_BACKEND_URL=${VITE_BACKEND_URL:-http://localhost:8000}
VITE_NODE_ENV=development
EOF
    echo "✅ Created frontend/.env.local file"
else
    echo "✅ frontend/.env.local file already exists"
fi

echo ""
echo "🔧 Setup complete! Next steps:"
echo "1. Edit backend/.env and add your OpenAI API key"
echo "2. Run: docker-compose up --build"
echo "3. Open http://${SERVER_IP:-localhost}:3000 in your browser"
echo ""
echo "📚 For more help, see SETUP.md"
