from src.application.services.language_service import LanguageDetectionService
from src.application.services.speaker_service import SpeakerMatchingService
from src.domain.enums import JobStatus
from src.infrastructure.db.models import SpeakerAliasORM, TranscriptSegmentORM
from src.infrastructure.whisperx.speaker_embeddings import SpeakerEmbeddingService


class ProcessingCancelled(Exception):
    pass


class ProcessingService:
    def __init__(self, uow_factory, processor, embedder, logger, threshold):
        self.uow_factory = uow_factory
        self.processor = processor
        self.embedder = embedder
        self.logger = logger
        self.threshold = threshold

    async def _ensure_not_cancelled(self, job_id):
        async with self.uow_factory() as uow:
            if await uow.repo.is_cancel_requested(job_id):
                raise ProcessingCancelled()

    async def process(self, job_id):
        async with self.uow_factory() as uow:
            job = await uow.repo.get_job(job_id)
            await uow.repo.update_job(
                job_id, status="PROCESSING", progress_percent=1, current_step="ProcessingStarted"
            )
        await self.logger.emit(job_id, "ProcessingStarted", "Обработка началась", 1)
        try:
            await self._ensure_not_cancelled(job_id)
            result = self.processor.process(job.stored_file_path)
            await self.logger.emit(job_id, "TranscriptionCompleted", "ASR/alignment/diarization завершены", 35)
            if not result["segments"]:
                await self.logger.emit(job_id, "NoSpeechDetected", "Речь не найдена", 90)

            await self._ensure_not_cancelled(job_id)
            lang_service = LanguageDetectionService()
            languages = lang_service.detected_languages(result["segments"])
            await self.logger.emit(job_id, "LanguagesDetected", "Определены языки", 50, {"languages": languages})

            spk = SpeakerEmbeddingService()
            labels = sorted({s.get("speaker", "SPEAKER_00") for s in result["segments"]})
            vectors = {
                label: spk.embedding_for_label(job.stored_file_path, label, result["segments"])
                for label in labels
            }
            matcher = SpeakerMatchingService(self.threshold)

            async with self.uow_factory() as uow:
                known_speakers = await uow.repo.all_speakers()
                speaker_names = {}
                for label, vector in vectors.items():
                    matched, score = matcher.match(vector, known_speakers)
                    speaker_names[label] = matched.speaker_name if matched else None
                    await self.logger.emit(
                        job_id,
                        "SpeakerMatched" if matched else "SpeakerMatchSkipped",
                        f"{label}: similarity={score:.3f}",
                        62,
                        {"speaker_label": label, "speaker_name": speaker_names[label], "score": score},
                    )
                segs = [
                    TranscriptSegmentORM(
                        job_id=job_id,
                        filename=job.display_filename,
                        uploaded_at=job.uploaded_at,
                        status=JobStatus.SUCCESS.value,
                        start_seconds=float(s.get("start", 0)),
                        end_seconds=float(s.get("end", 0)),
                        language=s.get("language") or result.get("language") or "unknown",
                        text=s.get("text", ""),
                        speaker_label=s.get("speaker", "SPEAKER_00"),
                        speaker_name=speaker_names.get(s.get("speaker", "SPEAKER_00")),
                        speaker_vector=vectors.get(s.get("speaker", "SPEAKER_00")),
                    )
                    for s in result["segments"]
                ]
                await uow.repo.add_segments(segs)
                for label, vec in vectors.items():
                    uow.session.add(
                        SpeakerAliasORM(
                            job_id=job_id,
                            speaker_label=label,
                            speaker_name=speaker_names.get(label),
                            speaker_vector=vec,
                        )
                    )
                await uow.repo.update_job(
                    job_id,
                    progress_percent=70,
                    current_step="SegmentsPersisted",
                    detected_languages=languages,
                    duration_seconds=result.get("duration_seconds"),
                )
            await self.logger.emit(job_id, "SegmentsPersisted", "Сегменты сохранены", 70)

            await self._ensure_not_cancelled(job_id)
            async with self.uow_factory() as uow:
                segments = await uow.repo.list_segments(job_id)
                texts = [s.text for s in segments]
                embeddings = await self.embedder.embed(texts) if texts else []
                await uow.repo.update_segment_embeddings(
                    {segment.id: embedding for segment, embedding in zip(segments, embeddings, strict=False)}
                )
                await uow.repo.update_job(
                    job_id, progress_percent=95, current_step="TranscriptIndexed"
                )
            await self.logger.emit(job_id, "TranscriptIndexed", "Текст проиндексирован в PGVector", 95)

            async with self.uow_factory() as uow:
                await uow.repo.update_job(
                    job_id,
                    status=JobStatus.SUCCESS.value,
                    progress_percent=100,
                    current_step="ProcessingSucceeded",
                )
            await self.logger.emit(job_id, "ProcessingSucceeded", "Обработка завершена", 100)
        except ProcessingCancelled:
            async with self.uow_factory() as uow:
                await uow.repo.update_job(
                    job_id, status=JobStatus.CANCELLED.value, current_step="ProcessingCancelled"
                )
            await self.logger.emit(job_id, "ProcessingCancelled", "Обработка отменена")
        except Exception as e:
            async with self.uow_factory() as uow:
                await uow.repo.update_job(
                    job_id,
                    status=JobStatus.ERROR.value,
                    error_message=str(e),
                    current_step="ProcessingFailed",
                )
            await self.logger.emit(job_id, "ProcessingFailed", "Ошибка обработки", None, {"error": str(e)})
