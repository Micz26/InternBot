# InternBot Frontend

A modern, responsive React frontend for the InternBot AI assistant, designed for recommending internships and job opportunities for students.

## Features

- 🎨 **Modern UI/UX**: Clean, aesthetic design with smooth animations
- 📱 **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- 🎯 **Focused on Internships**: Specialized for student internship recommendations
- 📍 **Location Services**: GPS integration for location-aware responses
- 🔔 **Toast Notifications**: User-friendly error and success messages
- ⚡ **Fast Performance**: Built with Vite for optimal development and build times
- 🐳 **Docker Ready**: Easy deployment with Docker containers

## Tech Stack

- **React 18** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **Axios** for API communication

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Development Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_BACKEND_URL=http://localhost:8000
VITE_NODE_ENV=development
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Docker Deployment

### Development with Docker

```bash
# From project root
docker-compose -f docker-compose.dev.yml up --build
```

### Production with Docker

```bash
# From project root
docker-compose up --build
```

## Platform Deployment

### Vercel

1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard:
   - `VITE_BACKEND_URL`: Your backend API URL
3. Deploy automatically on push to main branch

### Netlify

1. Connect your GitHub repository to Netlify
2. Set build command: `npm run build`
3. Set publish directory: `dist`
4. Set environment variables in Netlify dashboard
5. Deploy automatically on push to main branch

### Manual Deployment

1. Build the application:
   ```bash
   npm run build
   ```

2. Upload the `dist` folder to your web server

3. Configure your web server to serve the `index.html` for all routes (SPA routing)

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   └── Toast.tsx       # Toast notification system
│   ├── lib/                # Utility functions and constants
│   │   └── consts.ts       # API endpoints and configuration
│   ├── services/           # API services
│   │   └── chatService.ts  # Chat API integration
│   ├── views/              # Page components
│   │   └── Chat.tsx        # Main chat interface
│   ├── App.tsx             # Main app component
│   ├── App.css             # Global styles
│   └── main.tsx            # App entry point
├── public/                 # Static assets
├── Dockerfile              # Production Docker image
├── Dockerfile.dev          # Development Docker image
├── nginx.conf              # Nginx configuration
├── vercel.json             # Vercel deployment config
├── netlify.toml            # Netlify deployment config
└── package.json            # Dependencies and scripts
```

## API Integration

The frontend communicates with the backend through the following endpoints:

- `POST /agent/invoke` - Send chat message and get response
- `POST /agent/stream` - Stream chat responses (future feature)
- `POST /scrape/data` - Trigger data scraping (admin feature)

## Styling

The application uses Tailwind CSS with custom configuration:

- **Primary Colors**: Blue to Indigo gradient
- **Secondary Colors**: Gray scale
- **Custom Animations**: Fade-in, slide-up, pulse effects
- **Responsive Design**: Mobile-first approach

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
