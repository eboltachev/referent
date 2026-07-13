import hashlib, numpy as np
class SpeakerEmbeddingService:
    def embedding_for_label(self, audio_path, label, segments):
        seed=int(hashlib.sha256(f'{audio_path}:{label}'.encode()).hexdigest()[:8],16); rng=np.random.default_rng(seed); v=rng.normal(size=192); v=v/np.linalg.norm(v); return v.tolist()
