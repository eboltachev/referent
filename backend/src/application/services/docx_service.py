from datetime import datetime
def format_mmss(seconds: float) -> str:
    m,s=divmod(int(seconds),60); return f"{m:02d}:{s:02d}"
def docx_filename(job) -> str:
    if getattr(job,'source_type','') == 'RECORDING':
        dt=getattr(job,'recording_started_at',None) or getattr(job,'uploaded_at',datetime.utcnow())
        return f"recording_{dt:%Y-%m-%d_%H-%M}.docx"
    name=(getattr(job,'original_filename',None) or getattr(job,'display_filename','transcript')).rsplit('/',1)[-1]
    base=name.rsplit('.',1)[0]
    return f"{base}.docx"
