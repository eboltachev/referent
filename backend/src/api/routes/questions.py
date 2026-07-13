from uuid import UUID
from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse
from src.api.schemas import QuestionRequest
from src.infrastructure.db.session import get_session
from src.infrastructure.db.repositories import Repositories
from src.infrastructure.agents.graph import TranscriptAgentGraph, sse
router=APIRouter()
@router.post('/jobs/{job_id}/questions/stream')
async def question(job_id: UUID, body: QuestionRequest, session=Depends(get_session)):
    segments=await Repositories(session).list_segments(job_id)
    async def gen():
        async for event in TranscriptAgentGraph().stream(job_id, body.question, segments): yield sse(event)
    return EventSourceResponse(gen())
