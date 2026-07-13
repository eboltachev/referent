import os, subprocess
class WhisperXProductionProcessor:
    def __init__(self, model_name, device, compute_type, hf_token): self.model_name=model_name; self.device=device; self.compute_type=compute_type; self.hf_token=hf_token; self._model=None
    def _load(self):
        import whisperx
        if self._model is None: self._model=whisperx.load_model(self.model_name, self.device, compute_type=self.compute_type)
        return whisperx, self._model
    def prepare_audio(self, path):
        if os.path.splitext(path)[1].lower() in {'.mp4','.mov','.mkv','.avi'}:
            out=path+'.wav'; subprocess.run(['ffmpeg','-y','-i',path,'-vn','-acodec','pcm_s16le','-ar','16000','-ac','1',out], check=True); return out
        return path
    def process(self, file_path):
        whisperx, model=self._load(); audio_path=self.prepare_audio(file_path); audio=whisperx.load_audio(audio_path)
        result=model.transcribe(audio, batch_size=16)
        if not result.get('segments'): return {'segments': [], 'language': result.get('language','unknown'), 'duration_seconds': 0}
        align_model, metadata=whisperx.load_align_model(language_code=result['language'], device=self.device)
        aligned=whisperx.align(result['segments'], align_model, metadata, audio, self.device, return_char_alignments=False)
        diarize=whisperx.DiarizationPipeline(use_auth_token=self.hf_token, device=self.device)
        diarized=diarize(audio); final=whisperx.assign_word_speakers(diarized, aligned)
        return {'segments': final.get('segments', []), 'language': result.get('language','unknown'), 'duration_seconds': max((s.get('end',0) for s in final.get('segments',[])), default=0)}
