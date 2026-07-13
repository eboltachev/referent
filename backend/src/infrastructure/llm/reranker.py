import json
from tenacity import retry, stop_after_attempt, wait_exponential


class AsyncReranker:
    def __init__(self, client, model: str = "BAAI/bge-reranker-v2-m3"):
        self.client = client
        self.model = model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=5))
    async def rerank(self, query: str, docs: list[str]) -> list[int]:
        if not docs:
            return []
        # OpenAI-compatible gateways expose rerankers differently. Prefer a chat-compatible
        # JSON scoring contract so the adapter stays async and isolated from app code.
        prompt = {
            "query": query,
            "documents": [{"index": i, "text": doc[:2000]} for i, doc in enumerate(docs)],
            "instruction": "Return JSON only: {\"ranking\":[document indexes from most to least relevant]}.",
        }
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": json.dumps(prompt, ensure_ascii=False)}],
            temperature=0,
        )
        content = response.choices[0].message.content or "{}"
        try:
            ranking = json.loads(content).get("ranking", [])
            valid = [int(i) for i in ranking if isinstance(i, int) or str(i).isdigit()]
            return [i for i in valid if 0 <= i < len(docs)] or list(range(len(docs)))
        except json.JSONDecodeError:
            return list(range(len(docs)))
