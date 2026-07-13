from typing import Protocol
from uuid import UUID
class EventLogger(Protocol):
    async def emit(self, job_id: UUID, event_type: str, message: str, progress_percent: int | None=None, payload: dict | None=None) -> None: ...
