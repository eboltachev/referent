import asyncio, json
class EventBroker:
    def __init__(self): self.subscribers={}
    async def subscribe(self, job_id):
        q=asyncio.Queue(); self.subscribers.setdefault(str(job_id), set()).add(q); return q
    async def unsubscribe(self, job_id, q): self.subscribers.get(str(job_id), set()).discard(q)
    async def publish(self, job_id, event):
        for q in list(self.subscribers.get(str(job_id), [])): q.put_nowait(event)
broker=EventBroker()
