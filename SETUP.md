# InternBot Setup Guide

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API Key (for AI functionality)

### 1. Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/account/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the API key (starts with `sk-proj-`)

### 2. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# backend/.env
OPENAI_API_KEY=sk-proj-your-actual-openai-api-key-here
DB_HOST=db
DB_PORT=5432
DB_NAME=internbot
DB_USER=postgres
DB_PASSWORD=password
OFFERS_TABLE_NAME=offers
```

### 3. Start the Application

```bash
# Start all services
docker-compose up --build

# Or start in development mode
docker-compose -f docker-compose.dev.yml up --build
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Troubleshooting

### OpenAI API Key Error
If you see `401 - Invalid API key` error:
1. Make sure you have a valid OpenAI API key
2. Check that the `.env` file is in the `backend` directory
3. Restart the backend container: `docker-compose restart backend`

### Database Connection Issues
If the database fails to connect:
1. Make sure PostgreSQL is running
2. Check the database credentials in `.env`
3. Restart all services: `docker-compose down && docker-compose up --build`

### Frontend Not Loading
If the frontend shows errors:
1. Check that the backend is running on port 8000
2. Verify the `VITE_BACKEND_URL` environment variable
3. Check browser console for CORS errors

## 📝 Environment Variables Reference

### Backend (.env)
```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Database
DB_HOST=db
DB_PORT=5432
DB_NAME=internbot
DB_USER=postgres
DB_PASSWORD=password

# Optional
OFFERS_TABLE_NAME=offers
```

### Frontend (.env.local)
```env
VITE_BACKEND_URL=http://localhost:8000
VITE_NODE_ENV=development
```

## 🎯 Usage

1. **Start the application** using Docker Compose
2. **Open the frontend** at http://localhost:3000
3. **Ask questions** about internships and job opportunities
4. **The AI will help** you find relevant opportunities

## 🆘 Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify your OpenAI API key is valid
3. Ensure all environment variables are set correctly
4. Check the troubleshooting section above
