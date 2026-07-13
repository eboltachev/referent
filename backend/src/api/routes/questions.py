from uuid import UUID

from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

from src.api.schemas import QuestionRequest
from src.infrastructure.agents.graph import AgentDependencies, TranscriptAgentGraph, sse
from src.infrastructure.db.repositories import Repositories
from src.infrastructure.db.session import get_session
from src.infrastructure.llm.chat import AsyncChatClient
from src.infrastructure.llm.embeddings import AsyncEmbeddingClient
from src.infrastructure.llm.openai_async_client import OpenAIAsyncFactory
from src.infrastructure.llm.reranker import AsyncReranker

router = APIRouter()


@router.post("/jobs/{job_id}/questions/stream")
async def question(job_id: UUID, body: QuestionRequest, session=Depends(get_session)):
    repo = Repositories(session)
    client = OpenAIAsyncFactory().create()
    deps = AgentDependencies(
        repo=repo,
        embedder=AsyncEmbeddingClient(client),
        reranker=AsyncReranker(client),
        chat=AsyncChatClient(client),
    )

    async def gen():
        try:
            async for event in TranscriptAgentGraph(deps).stream(job_id, body.question):
                yield sse(event)
        finally:
            await client.close()

    return EventSourceResponse(gen())
