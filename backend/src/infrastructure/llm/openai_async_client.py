from openai import AsyncOpenAI, DefaultAioHttpClient
from src.config import settings
class OpenAIAsyncFactory:
    def create(self): return AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url or None, http_client=DefaultAioHttpClient())
