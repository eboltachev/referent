class AsyncReranker:
    def __init__(self, client, model='BAAI/bge-reranker-v2-m3'): self.client=client; self.model=model
    async def rerank(self, query, docs): return list(range(len(docs)))
