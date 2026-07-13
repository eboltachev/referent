import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Float, Integer, ForeignKey, UniqueConstraint, JSON, text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import Vector
class Base(DeclarativeBase): pass
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
class ProcessingJobORM(Base, TimestampMixin):
    __tablename__="processing_jobs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    original_filename: Mapped[str|None] = mapped_column(Text)
    display_filename: Mapped[str] = mapped_column(Text, nullable=False)
    stored_file_path: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    recording_started_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    progress_percent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_step: Mapped[str|None] = mapped_column(Text)
    detected_languages: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, server_default=text("'{}'"))
    duration_seconds: Mapped[float|None] = mapped_column(Float)
    error_message: Mapped[str|None] = mapped_column(Text)
    cancel_requested: Mapped[bool] = mapped_column(default=False, nullable=False)
class TranscriptSegmentORM(Base, TimestampMixin):
    __tablename__="transcript_segments"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("processing_jobs.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    start_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    end_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    language: Mapped[str] = mapped_column(Text, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    speaker_label: Mapped[str] = mapped_column(Text, nullable=False)
    speaker_name: Mapped[str|None] = mapped_column(Text)
    speaker_vector = mapped_column(Vector(192))
    text_embedding = mapped_column(Vector(768))
class SpeakerORM(Base, TimestampMixin):
    __tablename__="speakers"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    speaker_name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    speaker_vector = mapped_column(Vector(192), nullable=False)
    samples_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
class SpeakerAliasORM(Base, TimestampMixin):
    __tablename__="speaker_aliases"; __table_args__=(UniqueConstraint("job_id","speaker_label"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("processing_jobs.id", ondelete="CASCADE"))
    speaker_label: Mapped[str] = mapped_column(Text, nullable=False)
    speaker_name: Mapped[str|None] = mapped_column(Text)
    speaker_vector = mapped_column(Vector(192))
class ProcessingEventORM(Base):
    __tablename__="processing_events"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("processing_jobs.id", ondelete="CASCADE"), index=True)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    progress_percent: Mapped[int|None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
class AgentMessageORM(Base):
    __tablename__="agent_messages"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("processing_jobs.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(Text, nullable=False); content: Mapped[str] = mapped_column(Text, nullable=False)
    tool_name: Mapped[str|None] = mapped_column(Text); payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
