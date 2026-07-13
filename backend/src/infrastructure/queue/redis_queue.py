from uuid import UUID
import redis.asyncio as redis
class RedisJobQueue:
    def __init__(self, url: str): self.redis=redis.from_url(url, decode_responses=True); self.key='jobs'
    async def enqueue(self, job_id: UUID): await self.redis.lpush(self.key, str(job_id))
    async def dequeue(self, timeout: int=5):
        item=await self.redis.brpop(self.key, timeout=timeout)
        return UUID(item[1]) if item else None
