import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.api.routes import uploads, recordings, jobs, speakers, questions, downloads
from src.infrastructure.logging.async_event_logger import AsyncEventLogger
app=FastAPI(title='Интеллектуальная Стенограмма')
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins.split(','), allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
for r in [uploads.router, recordings.router, jobs.router, speakers.router, questions.router, downloads.router]: app.include_router(r, prefix='/api')
@app.get('/health')
async def health(): return {'status':'ok'}
@app.on_event('startup')
async def startup():
    app.state.event_logger=AsyncEventLogger(); app.state.flusher_task=asyncio.create_task(app.state.event_logger.flusher())
