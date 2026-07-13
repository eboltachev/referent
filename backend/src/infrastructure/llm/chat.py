from collections.abc import AsyncIterator
from tenacity import retry, stop_after_attempt, wait_exponential


class AsyncChatClient:
    def __init__(self, client, model: str = "openai/gpt-oss-120b"):
        self.client = client
        self.model = model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=5))
    async def complete(self, messages: list[dict[str, str]], temperature: float = 0.1) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

    async def stream(self, messages: list[dict[str, str]], temperature: float = 0.1) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
