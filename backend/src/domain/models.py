from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from .enums import JobStatus, SourceType
from .errors import InvalidStatusTransition
@dataclass
class ProcessingJob:
    source_type: SourceType
    display_filename: str
    stored_file_path: str
    id: UUID = field(default_factory=uuid4)
    status: JobStatus = JobStatus.PENDING
    progress_percent: int = 0
    current_step: str | None = None
    uploaded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    def transition(self, status: JobStatus) -> None:
        allowed={JobStatus.PENDING:{JobStatus.PROCESSING,JobStatus.CANCELLED,JobStatus.ERROR},JobStatus.PROCESSING:{JobStatus.SUCCESS,JobStatus.ERROR,JobStatus.CANCELLED},JobStatus.SUCCESS:set(),JobStatus.ERROR:set(),JobStatus.CANCELLED:set()}
        if status not in allowed[self.status]: raise InvalidStatusTransition(f"{self.status}->{status}")
        self.status=status
@dataclass
class TranscriptSegment:
    job_id: UUID; filename: str; start_seconds: float; end_seconds: float; language: str; text: str; speaker_label: str; speaker_name: str | None=None
    id: UUID = field(default_factory=uuid4)
