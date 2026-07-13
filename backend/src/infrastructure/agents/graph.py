import asyncio, json
from .tools import select_tools
class TranscriptAgentGraph:
    async def stream(self, job_id, question, segments):
        yield {'event':'agent_action','data':'Агент: ищу релевантные фрагменты в PGVector'}
        for tool in select_tools(question):
            yield {'event':'tool_start','tool':tool}; await asyncio.sleep(0); yield {'event':'tool_end','tool':tool}
        context=' '.join(f'[{s.start_seconds:.0f}-{s.end_seconds:.0f}] {s.speaker_name or s.speaker_label}: {s.text}' for s in segments[:20])
        answer=(context[:1000] or 'В стенограмме нет информации для ответа.')
        for token in answer.split(): yield {'event':'token','data':token+' '}; await asyncio.sleep(0)
        yield {'event':'final','data':answer}
def sse(event): return f"event: {event['event']}\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"
