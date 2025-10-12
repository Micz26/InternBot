# Server Configuration

This project now uses centralized server configuration to avoid hardcoding the server IP address in multiple files.

## Configuration File

The main configuration is stored in `config.env`:

```bash
# Server Configuration
SERVER_IP=<your_server_ip>
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Backend URL (automatically constructed from SERVER_IP and BACKEND_PORT)
VITE_BACKEND_URL=http://<your_server_ip>:8000
```

## How to Change Server IP

To change the server IP address, simply update the `SERVER_IP` variable in `config.env`:

```bash
# Edit config.env
SERVER_IP=your.new.server.ip
VITE_BACKEND_URL=http://your.new.server.ip:8000
```

## Files That Use the Configuration

The following files now reference the centralized configuration:

1. **Backend Settings** (`backend/src/intern_bot/settings/settings.py`)
   - CORS configuration uses `SERVER_IP` and `FRONTEND_PORT`

2. **Docker Compose Files** (`docker-compose.yml`, `docker-compose.dev.yml`)
   - Frontend environment uses `VITE_BACKEND_URL` with fallback

3. **Frontend Configuration** (`frontend/vite.config.ts`)
   - Proxy target uses `VITE_BACKEND_URL` environment variable

4. **Nginx Configuration** (`frontend/nginx.conf`)
   - Server name uses `SERVER_IP` with fallback

5. **Setup Script** (`setup.sh`)
   - Loads configuration from `config.env` and uses it for setup

## Environment Variables

The following environment variables are used:

- `SERVER_IP`: The main server IP address
- `BACKEND_PORT`: Backend service port (default: 8000)
- `FRONTEND_PORT`: Frontend service port (default: 3000)
- `VITE_BACKEND_URL`: Complete backend URL for frontend

## Fallback Values

All configurations include fallback values to ensure the application works even if the configuration file is missing:

- Default `SERVER_IP`: `<your_server_ip>`
- Default `VITE_BACKEND_URL`: `http://<your_server_ip>:8000`

## Usage

1. **For Development**: Update `config.env` and run `./setup.sh`
2. **For Production**: Set environment variables or update `config.env` before deployment
3. **For Docker**: Environment variables are automatically loaded from `config.env` if present
