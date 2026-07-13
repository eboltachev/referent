import math, numpy as np
def cosine_similarity(a: list[float], b: list[float]) -> float:
    den=math.sqrt(sum(x*x for x in a))*math.sqrt(sum(x*x for x in b)); return 0.0 if den==0 else sum(x*y for x,y in zip(a,b))/den
class SpeakerMatchingService:
    def __init__(self, threshold: float): self.threshold=threshold
    def match(self, vector, speakers):
        best=(None, -1.0)
        for s in speakers:
            score=cosine_similarity(vector, s.speaker_vector)
            if score>best[1]: best=(s,score)
        return best if best[0] is not None and best[1] >= self.threshold else (None, best[1])
def weighted_average(old, old_count: int, new): return ((np.array(old)*old_count + np.array(new))/(old_count+1)).tolist()
