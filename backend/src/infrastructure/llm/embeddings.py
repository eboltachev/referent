from tenacity import retry, stop_after_attempt, wait_exponential
class AsyncEmbeddingClient:
    def __init__(self, client, model='nomic-ai/nomic-embed-text-v2-moe'): self.client=client; self.model=model
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=5))
    async def embed(self, texts):
        res=await self.client.embeddings.create(model=self.model, input=texts)
        return [d.embedding for d in res.data]
