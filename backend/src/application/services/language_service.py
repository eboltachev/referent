class LanguageDetectionService:
    def detected_languages(self, segments):
        langs={s.get('language') if isinstance(s,dict) else s.language for s in segments if (s.get('language') if isinstance(s,dict) else s.language)}
        return sorted(langs or {'unknown'})
    def correction_for_segment(self, segment, detected: set[str]):
        text = segment.get('text','') if isinstance(segment,dict) else segment.text
        if len(text.strip()) < 3: return None
        if any('а' <= ch.lower() <= 'я' for ch in text): return 'ru' if 'ru' in detected else None
        return 'en' if 'en' in detected else None
