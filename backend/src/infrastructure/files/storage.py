import os, uuid, aiofiles
from fastapi import UploadFile
SUPPORTED={'.wav','.mp3','.m4a','.flac','.ogg','.webm','.mp4','.mov','.mkv','.avi'}
class FileStorage:
    def __init__(self, root: str): self.root=root; os.makedirs(root, exist_ok=True)
    async def save_upload(self, file: UploadFile) -> str:
        ext=os.path.splitext(file.filename or '')[1].lower()
        if ext not in SUPPORTED: raise ValueError('unsupported file type')
        path=os.path.join(self.root, f"{uuid.uuid4()}{ext}")
        async with aiofiles.open(path,'wb') as out:
            while chunk:=await file.read(1024*1024): await out.write(chunk)
        return path
