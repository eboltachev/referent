from uuid import UUID
from fastapi import APIRouter, Depends
from src.api.schemas import SpeakerPatch
from src.infrastructure.db.session import get_session
from src.infrastructure.db.repositories import Repositories
router=APIRouter()
@router.patch('/jobs/{job_id}/speakers/{speaker_label}')
async def patch_speaker(job_id: UUID, speaker_label: str, body: SpeakerPatch, session=Depends(get_session)):
    await Repositories(session).upsert_speaker_name(job_id, speaker_label, body.speaker_name or '')
    await session.commit(); return {'speaker_label':speaker_label,'speaker_name':body.speaker_name}
