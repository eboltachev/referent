from types import SimpleNamespace
import pytest
from src.application.services.speaker_service import cosine_similarity, SpeakerMatchingService, weighted_average
from src.application.services.language_service import LanguageDetectionService
from src.application.services.docx_service import format_mmss, docx_filename
from src.domain.models import ProcessingJob
from src.domain.enums import SourceType, JobStatus
from src.domain.errors import InvalidStatusTransition
from src.infrastructure.agents.tools import select_tools

def test_language_correction_service():
    svc=LanguageDetectionService(); assert svc.detected_languages([{'language':'ru'}])==['ru']; assert svc.correction_for_segment({'text':'привет'}, {'ru'})=='ru'
def test_speaker_matching_threshold():
    sp=SimpleNamespace(speaker_vector=[1,0], speaker_name='A'); assert SpeakerMatchingService(.8).match([1,0],[sp])[0] is sp; assert SpeakerMatchingService(.8).match([0,1],[sp])[0] is None
def test_weighted_average(): assert weighted_average([1,1],1,[3,3]) == [2,2]
@pytest.mark.asyncio
async def test_async_event_logger_nonblocking():
    from src.infrastructure.logging.async_event_logger import AsyncEventLogger
    import uuid
    logger=AsyncEventLogger(); await logger.emit(uuid.uuid4(),'FileUploaded','ok'); assert logger.queue.qsize()==1
def test_docx_filename_and_time():
    assert format_mmss(65)=='01:05'; assert docx_filename(SimpleNamespace(source_type='UPLOAD', original_filename='a.mp3', display_filename='a.mp3'))=='a.docx'
def test_domain_status_transitions():
    j=ProcessingJob(SourceType.UPLOAD,'a','/tmp/a'); j.transition(JobStatus.PROCESSING); j.transition(JobStatus.SUCCESS); 
    with pytest.raises(InvalidStatusTransition): j.transition(JobStatus.ERROR)
def test_agent_tool_selection_contract(): assert 'calculator' in select_tools('сколько человек')
