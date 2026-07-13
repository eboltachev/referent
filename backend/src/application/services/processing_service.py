from src.domain.enums import JobStatus
from src.infrastructure.db.models import TranscriptSegmentORM, SpeakerAliasORM
from src.infrastructure.whisperx.speaker_embeddings import SpeakerEmbeddingService
from src.application.services.language_service import LanguageDetectionService
class ProcessingService:
    def __init__(self, uow_factory, processor, embedder, logger, threshold): self.uow_factory=uow_factory; self.processor=processor; self.embedder=embedder; self.logger=logger; self.threshold=threshold
    async def process(self, job_id):
        async with self.uow_factory() as uow:
            job=await uow.repo.get_job(job_id); await uow.repo.update_job(job_id, status='PROCESSING', progress_percent=1, current_step='ProcessingStarted')
        await self.logger.emit(job_id,'ProcessingStarted','Обработка началась',1)
        try:
            result=self.processor.process(job.stored_file_path)
            await self.logger.emit(job_id,'TranscriptionCompleted','ASR завершен',35)
            if not result['segments']: await self.logger.emit(job_id,'NoSpeechDetected','Речь не найдена',90)
            lang_service=LanguageDetectionService(); languages=lang_service.detected_languages(result['segments'])
            spk=SpeakerEmbeddingService(); labels=sorted({s.get('speaker','SPEAKER_00') for s in result['segments']})
            vectors={l:spk.embedding_for_label(job.stored_file_path,l,result['segments']) for l in labels}
            async with self.uow_factory() as uow:
                job=await uow.repo.get_job(job_id)
                segs=[TranscriptSegmentORM(job_id=job_id, filename=job.display_filename, uploaded_at=job.uploaded_at, status='SUCCESS', start_seconds=float(s.get('start',0)), end_seconds=float(s.get('end',0)), language=s.get('language') or result.get('language') or 'unknown', text=s.get('text',''), speaker_label=s.get('speaker','SPEAKER_00'), speaker_vector=vectors.get(s.get('speaker','SPEAKER_00'))) for s in result['segments']]
                await uow.repo.add_segments(segs)
                for label, vec in vectors.items(): uow.session.add(SpeakerAliasORM(job_id=job_id, speaker_label=label, speaker_vector=vec))
                await uow.repo.update_job(job_id, status='SUCCESS', progress_percent=100, current_step='ProcessingSucceeded', detected_languages=languages, duration_seconds=result.get('duration_seconds'))
            await self.logger.emit(job_id,'ProcessingSucceeded','Обработка завершена',100)
        except Exception as e:
            async with self.uow_factory() as uow: await uow.repo.update_job(job_id, status='ERROR', error_message=str(e), current_step='ProcessingFailed')
            await self.logger.emit(job_id,'ProcessingFailed','Ошибка обработки',None, {'error':str(e)})
