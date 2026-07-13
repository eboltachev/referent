import uuid, numpy as np
from datetime import datetime, timezone
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from .models import ProcessingJobORM, TranscriptSegmentORM, SpeakerORM, SpeakerAliasORM, ProcessingEventORM
class Repositories:
    def __init__(self, session: AsyncSession): self.session=session
    async def create_job(self, source_type, display_filename, stored_file_path, original_filename=None, recording_started_at=None):
        job=ProcessingJobORM(id=uuid.uuid4(), source_type=source_type, original_filename=original_filename, display_filename=display_filename, stored_file_path=stored_file_path, uploaded_at=datetime.now(timezone.utc), recording_started_at=recording_started_at, status="PENDING", progress_percent=0)
        self.session.add(job); await self.session.flush(); return job
    async def get_job(self, job_id): return await self.session.get(ProcessingJobORM, job_id)
    async def update_job(self, job_id, **kw): await self.session.execute(update(ProcessingJobORM).where(ProcessingJobORM.id==job_id).values(**kw))
    async def add_segments(self, segments): self.session.add_all(segments); await self.session.flush()
    async def list_segments(self, job_id): return list((await self.session.execute(select(TranscriptSegmentORM).where(TranscriptSegmentORM.job_id==job_id).order_by(TranscriptSegmentORM.start_seconds))).scalars())
    async def list_aliases(self, job_id): return list((await self.session.execute(select(SpeakerAliasORM).where(SpeakerAliasORM.job_id==job_id).order_by(SpeakerAliasORM.speaker_label))).scalars())
    async def add_event(self, event): self.session.add(event)
    async def speaker_by_name(self, name): return (await self.session.execute(select(SpeakerORM).where(SpeakerORM.speaker_name==name))).scalar_one_or_none()
    async def all_speakers(self): return list((await self.session.execute(select(SpeakerORM))).scalars())
    async def upsert_speaker_name(self, job_id, label, name):
        segs=await self.list_segments(job_id); vectors=[s.speaker_vector for s in segs if s.speaker_label==label and s.speaker_vector]
        avg=(np.mean(np.array(vectors), axis=0).tolist() if vectors else [0.0]*192)
        await self.session.execute(update(TranscriptSegmentORM).where(TranscriptSegmentORM.job_id==job_id, TranscriptSegmentORM.speaker_label==label).values(speaker_name=name or None))
        alias=(await self.session.execute(select(SpeakerAliasORM).where(SpeakerAliasORM.job_id==job_id, SpeakerAliasORM.speaker_label==label))).scalar_one_or_none()
        if not alias: self.session.add(SpeakerAliasORM(job_id=job_id, speaker_label=label, speaker_name=name or None, speaker_vector=avg))
        else: alias.speaker_name=name or None; alias.speaker_vector=avg
        if name:
            speaker=await self.speaker_by_name(name)
            if not speaker: self.session.add(SpeakerORM(speaker_name=name, speaker_vector=avg, samples_count=1))
            else:
                n=speaker.samples_count; speaker.speaker_vector=((np.array(speaker.speaker_vector)*n+np.array(avg))/(n+1)).tolist(); speaker.samples_count=n+1
