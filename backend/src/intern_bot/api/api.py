from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from intern_bot.api.utils.routes import router
from intern_bot.api.utils.scheduler import start_scheduler, stop_scheduler
from intern_bot.settings.settings import Settings

# Initialize settings
settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:3000',  # Keep for local development
        f'http://{settings.SERVER_IP}:{settings.FRONTEND_PORT}',  # Use settings for server IP
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(router)

