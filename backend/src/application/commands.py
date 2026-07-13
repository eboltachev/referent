from dataclasses import dataclass
from uuid import UUID
from src.domain.enums import SourceType
@dataclass(frozen=True)
class CreateJobCommand:
    source_type: SourceType; display_filename: str; stored_file_path: str; original_filename: str | None=None
@dataclass(frozen=True)
class ProcessJobCommand: job_id: UUID
