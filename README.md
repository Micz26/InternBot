# InternBot

An AI-powered assistant for recommending internships and job opportunities for students, designed to help users find the perfect internship or job placement.

## 🚀 Features

- **AI Chat Interface**: Modern, responsive chat interface with real-time communication
- **Job Scraping**: Automated scraping of job offers from multiple sources (PWR, Nokia, SII)
- **Location Services**: GPS integration for location-aware responses
- **Student-Focused**: Specialized recommendations for student internships
- **Real-time Updates**: Live data scraping and vector search
- **Modern UI/UX**: Clean, aesthetic design with smooth animations

## 🏗️ Architecture

The project consists of three main components:

### Backend (FastAPI + Python)
- **API Server**: FastAPI-based REST API
- **AI Agent**: LangChain-powered conversational AI
- **Data Scraping**: Automated job offer collection from multiple sources
- **Vector Database**: PostgreSQL with pgvector for semantic search
- **Data Management**: Efficient storage and retrieval of job offers

### Frontend (React + TypeScript)
- **Modern UI**: React 18 with TypeScript and Tailwind CSS
- **Responsive Design**: Mobile-first approach with smooth animations
- **Real-time Chat**: WebSocket-like experience with streaming responses
- **Audio Integration**: Text-to-speech and voice input capabilities
- **Toast Notifications**: User-friendly feedback system

### Database (PostgreSQL + pgvector)
- **Vector Storage**: Semantic search capabilities
- **Job Offers**: Structured storage of scraped opportunities
- **Metadata**: Rich information about each job posting

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **LangChain**: AI agent framework
- **PostgreSQL**: Primary database
- **pgvector**: Vector similarity search
- **Docker**: Containerization

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tooling
- **Tailwind CSS**: Styling
- **Axios**: HTTP client
- **Lucide React**: Icons

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.9+ (for local development)

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd InternBot
   ```

2. **Start with Docker Compose:**
   ```bash
   # Production setup
   docker-compose up --build
   
   # Development setup with hot reload
   docker-compose -f docker-compose.dev.yml up --build
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Database: localhost:5432

### Local Development

#### Backend
```bash
cd backend
pip install -e .
uvicorn intern_bot.api.api:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
InternBot/
├── backend/                 # FastAPI backend
│   ├── src/intern_bot/
│   │   ├── agent/          # AI agent implementation
│   │   ├── api/            # API routes and models
│   │   ├── data_scraper/   # Web scraping modules
│   │   ├── data_manager/   # Database operations
│   │   └── settings/       # Configuration
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── views/          # Page components
│   │   ├── services/       # API services
│   │   └── lib/            # Utilities
│   ├── Dockerfile
│   └── package.json
├── postgres/               # Database schema
├── docker-compose.yml      # Production setup
├── docker-compose.dev.yml  # Development setup
└── README.md
```

## 🌐 Deployment

### Platform Options

#### 1. Vercel (Frontend) + Railway/Render (Backend)
- **Frontend**: Deploy to Vercel with automatic builds
- **Backend**: Deploy to Railway or Render
- **Database**: Use managed PostgreSQL with pgvector

#### 2. Netlify (Frontend) + DigitalOcean (Backend)
- **Frontend**: Deploy to Netlify
- **Backend**: Deploy to DigitalOcean App Platform
- **Database**: Managed PostgreSQL droplet

#### 3. Full Docker Deployment
- **VPS**: Deploy entire stack on a VPS
- **Cloud**: Use cloud providers (AWS, GCP, Azure)
- **Orchestration**: Docker Swarm or Kubernetes

### Environment Variables

#### Backend
```env
DB_HOST=your-db-host
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your-password
DB_NAME=internbot
```

#### Frontend
```env
VITE_BACKEND_URL=https://your-backend-url.com
VITE_NODE_ENV=production
```

## 🔧 Configuration

### Data Sources
The system scrapes job offers from:
- **PWR (Politechnika Wrocławska)**: Academic job board
- **Nokia**: Corporate career portal
- **SII**: IT consulting company

### API Endpoints
- `POST /agent/invoke` - Chat with AI agent
- `POST /agent/stream` - Stream chat responses
- `POST /scrape/data` - Trigger data scraping

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation in each component's README
- Review the API documentation at `/docs` when running the backend

## 🔮 Future Enhancements

- [ ] Real-time notifications
- [ ] Advanced filtering and search
- [ ] User authentication and profiles
- [ ] Mobile app (React Native)
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Integration with more job boards
- [ ] Machine learning for job matching