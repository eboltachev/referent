class TranscriptQueryService:
    async def summarize(self, segments): return ' '.join(s.text for s in segments)[:1000]
