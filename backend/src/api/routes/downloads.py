import os, tempfile
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from src.infrastructure.db.session import get_session
from src.infrastructure.db.repositories import Repositories
from src.infrastructure.files.docx_export import build_docx
from src.application.services.docx_service import docx_filename
router=APIRouter()
@router.get('/jobs/{job_id}/download')
async def download(job_id: UUID, session=Depends(get_session)):
    repo=Repositories(session); job=await repo.get_job(job_id)
    if not job: raise HTTPException(404)
    path=os.path.join(tempfile.gettempdir(), docx_filename(job)); build_docx(path, job, await repo.list_aliases(job_id), await repo.list_segments(job_id))
    return FileResponse(path, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename=docx_filename(job))
