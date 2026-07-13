from pydantic import BaseModel
from uuid import UUID
class JobCreated(BaseModel): job_id: UUID; status: str
class SpeakerPatch(BaseModel): speaker_name: str | None = None
class QuestionRequest(BaseModel): question: str
