from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, Depends
from src.config import settings
from src.domain.enums import SourceType
from src.infrastructure.files.storage import FileStorage
from src.infrastructure.db.session import get_session
from src.infrastructure.db.repositories import Repositories
from src.infrastructure.queue.redis_queue import RedisJobQueue
from src.api.schemas import JobCreated
router=APIRouter()
@router.post('/recordings', response_model=JobCreated)
async def recording(file: UploadFile, session=Depends(get_session)):
    path=await FileStorage(settings.uploads_dir).save_upload(file); now=datetime.now(timezone.utc)
    repo=Repositories(session); job=await repo.create_job(SourceType.RECORDING.value, file.filename or 'recording.webm', path, file.filename, now); await session.commit(); await RedisJobQueue(settings.redis_url).enqueue(job.id)
    return JobCreated(job_id=job.id, status=job.status)
