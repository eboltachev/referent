import asyncio, json
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from src.infrastructure.db.session import get_session
from src.infrastructure.db.repositories import Repositories
from src.infrastructure.logging.websocket_broker import broker
router=APIRouter()
@router.get('/jobs/{job_id}')
async def get_job(job_id: UUID, session=Depends(get_session)):
    job=await Repositories(session).get_job(job_id)
    if not job: raise HTTPException(404)
    return {'id':job.id,'status':job.status,'progress_percent':job.progress_percent,'current_step':job.current_step,'detected_languages':job.detected_languages,'error_message':job.error_message}
@router.post('/jobs/{job_id}/cancel')
async def cancel(job_id: UUID, session=Depends(get_session)):
    await Repositories(session).update_job(job_id, cancel_requested=True, status='CANCELLED', current_step='ProcessingCancelled'); await session.commit(); return {'status':'CANCELLED'}
@router.get('/jobs/{job_id}/results')
async def results(job_id: UUID, session=Depends(get_session)):
    repo=Repositories(session); return {'speakers':[{'speaker_label':a.speaker_label,'speaker_name':a.speaker_name} for a in await repo.list_aliases(job_id)], 'segments':[{'id':s.id,'speaker_label':s.speaker_label,'speaker_name':s.speaker_name,'start_seconds':s.start_seconds,'end_seconds':s.end_seconds,'language':s.language,'text':s.text} for s in await repo.list_segments(job_id)]}
@router.get('/jobs/{job_id}/events')
async def events(job_id: UUID):
    async def gen():
        q=await broker.subscribe(job_id)
        try:
            while True:
                event=await q.get(); yield {'event':event['event_type'], 'data':json.dumps(event, ensure_ascii=False)}
        finally: await broker.unsubscribe(job_id, q)
    return EventSourceResponse(gen())
