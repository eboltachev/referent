def test_import_models():
    from src.infrastructure.db.models import ProcessingJobORM, TranscriptSegmentORM
    assert ProcessingJobORM.__tablename__ == 'processing_jobs'
    assert TranscriptSegmentORM.__tablename__ == 'transcript_segments'
