# Deployment Guide

This guide covers different deployment options for the InternBot application.

## 🚀 Quick Deployment Options

### Option 1: Vercel (Frontend) + Railway (Backend) - Recommended

**Best for**: Easy deployment with automatic scaling

#### Frontend on Vercel
1. **Connect Repository**:
   - Go to [Vercel](https://vercel.com)
   - Import your GitHub repository
   - Select the `frontend` folder as root directory

2. **Configure Environment Variables**:
   ```
   VITE_BACKEND_URL=https://your-backend-url.railway.app
   VITE_NODE_ENV=production
   ```

3. **Deploy**: Vercel will automatically build and deploy

#### Backend on Railway
1. **Connect Repository**:
   - Go to [Railway](https://railway.app)
   - Connect your GitHub repository
   - Select the `backend` folder

2. **Add Database**:
   - Add PostgreSQL service
   - Enable pgvector extension

3. **Configure Environment Variables**:
   ```
   DB_HOST=your-db-host
   DB_PORT=5432
   DB_USER=postgres
   DB_PASSWORD=your-password
   DB_NAME=internbot
   ```

4. **Deploy**: Railway will automatically build and deploy

### Option 2: Netlify (Frontend) + DigitalOcean (Backend)

**Best for**: Cost-effective solution with good performance

#### Frontend on Netlify
1. **Connect Repository**:
   - Go to [Netlify](https://netlify.com)
   - Connect your GitHub repository
   - Set build command: `cd frontend && npm run build`
   - Set publish directory: `frontend/dist`

2. **Configure Environment Variables**:
   ```
   VITE_BACKEND_URL=https://your-backend-url.com
   ```

#### Backend on DigitalOcean App Platform
1. **Create App**:
   - Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
   - Create new app from GitHub
   - Select backend folder

2. **Add Database**:
   - Add managed PostgreSQL database
   - Enable pgvector extension

3. **Configure Environment Variables**:
   ```
   DB_HOST=your-db-host
   DB_PORT=5432
   DB_USER=postgres
   DB_PASSWORD=your-password
   DB_NAME=internbot
   ```

### Option 3: Full Docker Deployment

**Best for**: Complete control and custom infrastructure

#### VPS Deployment
1. **Prepare VPS**:
   ```bash
   # Install Docker and Docker Compose
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   sudo usermod -aG docker $USER
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Deploy Application**:
   ```bash
   # Clone repository
   git clone <your-repo-url>
   cd InternBot
   
   # Configure environment variables
   cp .env.example .env
   # Edit .env with your configuration
   
   # Start services
   docker-compose up -d --build
   ```

3. **Configure Reverse Proxy** (Nginx):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /api/ {
           proxy_pass http://localhost:8000/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

#### Cloud Provider Deployment

##### AWS
- **ECS**: Use ECS with Fargate for container orchestration
- **EC2**: Deploy on EC2 instances with Docker
- **RDS**: Use RDS PostgreSQL with pgvector

##### Google Cloud
- **Cloud Run**: Serverless container deployment
- **GKE**: Kubernetes cluster deployment
- **Cloud SQL**: Managed PostgreSQL with pgvector

##### Azure
- **Container Instances**: Simple container deployment
- **AKS**: Kubernetes service
- **Azure Database**: Managed PostgreSQL

## 🔧 Environment Configuration

### Backend Environment Variables
```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your-password
DB_NAME=internbot

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Security
SECRET_KEY=your-secret-key
```

### Frontend Environment Variables
```env
# API Configuration
VITE_BACKEND_URL=https://your-backend-url.com
VITE_NODE_ENV=production

# Optional: Analytics
VITE_GA_TRACKING_ID=your-ga-id
```

## 📊 Monitoring and Maintenance

### Health Checks
- **Frontend**: `GET /` - Should return 200
- **Backend**: `GET /health` - Should return 200
- **Database**: Connection test

### Logs
```bash
# Docker logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

## 🔒 Security Considerations

### SSL/TLS
- Use Let's Encrypt for free SSL certificates
- Configure HTTPS redirects
- Set secure headers

### Database Security
- Use strong passwords
- Enable SSL connections
- Restrict network access
- Regular backups

### API Security
- Rate limiting
- CORS configuration
- Input validation
- Error handling

## 📈 Performance Optimization

### Frontend
- Enable gzip compression
- Use CDN for static assets
- Implement caching strategies
- Optimize images

### Backend
- Database connection pooling
- Caching frequently accessed data
- Optimize database queries
- Use async/await properly

### Database
- Proper indexing
- Regular maintenance
- Connection pooling
- Query optimization

## 🆘 Troubleshooting

### Common Issues

#### Frontend not connecting to backend
- Check CORS configuration
- Verify backend URL in environment variables
- Check network connectivity

#### Database connection issues
- Verify database credentials
- Check network connectivity
- Ensure pgvector extension is installed

#### Build failures
- Check Node.js version compatibility
- Verify all dependencies are installed
- Check for TypeScript errors

### Debug Commands
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f [service-name]

# Access container shell
docker-compose exec [service-name] /bin/bash

# Check database connection
docker-compose exec db psql -U postgres -d internbot
```

## 📞 Support

For deployment issues:
1. Check the logs first
2. Verify environment variables
3. Test connectivity between services
4. Create an issue in the repository

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to production
        run: |
          # Your deployment commands here
```

This deployment guide should help you get your InternBot application running in production! 🚀
