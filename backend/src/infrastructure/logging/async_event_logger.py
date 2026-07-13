import asyncio, json
from datetime import datetime, timezone
from uuid import UUID
import redis.asyncio as redis
from src.infrastructure.db.session import AsyncSessionLocal
from src.infrastructure.db.models import ProcessingEventORM
from .websocket_broker import broker
class AsyncEventLogger:
    def __init__(self, redis_url: str|None=None):
        self.queue=asyncio.Queue(maxsize=10000); self.redis=redis.from_url(redis_url, decode_responses=True) if redis_url else None
    async def emit(self, job_id: UUID, event_type: str, message: str, progress_percent: int|None=None, payload: dict|None=None):
        event={'job_id':str(job_id),'event_type':event_type,'message':message,'progress_percent':progress_percent,'payload':payload or {},'created_at':datetime.now(timezone.utc).isoformat()}
        try: self.queue.put_nowait(event)
        except asyncio.QueueFull: pass
        if self.redis: await self.redis.xadd('processing_events', event | {'payload': json.dumps(event['payload'])})
        await broker.publish(job_id, event)
    async def flush_once(self):
        batch=[]
        while not self.queue.empty() and len(batch)<100: batch.append(await self.queue.get())
        if batch:
            async with AsyncSessionLocal() as s:
                for e in batch: s.add(ProcessingEventORM(job_id=UUID(e['job_id']), event_type=e['event_type'], message=e['message'], payload=e['payload'], progress_percent=e['progress_percent']))
                await s.commit()
    async def flusher(self):
        while True:
            await self.flush_once(); await asyncio.sleep(0.2)
