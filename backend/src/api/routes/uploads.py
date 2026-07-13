from fastapi import APIRouter, UploadFile, Depends, HTTPException
from src.config import settings
from src.domain.enums import SourceType
from src.infrastructure.files.storage import FileStorage
from src.infrastructure.db.session import get_session
from src.infrastructure.db.repositories import Repositories
from src.infrastructure.queue.redis_queue import RedisJobQueue
from src.api.schemas import JobCreated
router=APIRouter()
@router.post('/uploads', response_model=JobCreated)
async def upload(file: UploadFile, session=Depends(get_session)):
    try: path=await FileStorage(settings.uploads_dir).save_upload(file)
    except ValueError as e: raise HTTPException(400, str(e))
    repo=Repositories(session); job=await repo.create_job(SourceType.UPLOAD.value, file.filename or 'upload', path, file.filename); await session.commit()
    await RedisJobQueue(settings.redis_url).enqueue(job.id)
    return JobCreated(job_id=job.id, status=job.status)
