import asyncio, logging
from src.config import settings
from src.infrastructure.queue.redis_queue import RedisJobQueue
from src.infrastructure.db.uow import SqlAlchemyUnitOfWork
from src.infrastructure.whisperx.processor import WhisperXProductionProcessor
from src.infrastructure.llm.openai_async_client import OpenAIAsyncFactory
from src.infrastructure.llm.embeddings import AsyncEmbeddingClient
from src.infrastructure.logging.async_event_logger import AsyncEventLogger
from src.application.services.processing_service import ProcessingService
async def main():
    logging.basicConfig(level=logging.INFO); queue=RedisJobQueue(settings.redis_url); logger=AsyncEventLogger(settings.redis_url)
    client=OpenAIAsyncFactory().create(); embedder=AsyncEmbeddingClient(client)
    processor=WhisperXProductionProcessor(settings.whisperx_model, settings.whisperx_device, settings.whisperx_compute_type, settings.hf_token)
    service=ProcessingService(SqlAlchemyUnitOfWork, processor, embedder, logger, settings.speaker_match_threshold)
    while True:
        job_id=await queue.dequeue(5)
        if job_id: await service.process(job_id); await logger.flush_once()
if __name__=='__main__': asyncio.run(main())
