import json
from collections.abc import AsyncIterator
from dataclasses import dataclass

from src.infrastructure.agents.prompts import SYSTEM_PROMPT
from src.infrastructure.agents.tools import select_tools


def _segment_ref(segment) -> str:
    speaker = segment.speaker_name or segment.speaker_label
    return f"[{segment.start_seconds:.1f}–{segment.end_seconds:.1f}] {speaker}: {segment.text}"


@dataclass
class AgentDependencies:
    repo: object
    embedder: object
    reranker: object
    chat: object


class TranscriptAgentGraph:
    def __init__(self, deps: AgentDependencies | None = None):
        self.deps = deps

    async def stream(self, job_id, question: str, segments=None) -> AsyncIterator[dict]:
        yield {"event": "agent_action", "data": "Агент: планирую инструменты LangChain multi-agent"}
        tools = select_tools(question)
        for tool in tools:
            yield {"event": "tool_start", "tool": tool}
            yield {"event": "tool_end", "tool": tool}

        if self.deps:
            yield {"event": "agent_action", "data": "Агент: строю embedding вопроса и ищу фрагменты в PGVector"}
            query_embedding = (await self.deps.embedder.embed([question]))[0]
            candidates = await self.deps.repo.vector_search_segments(job_id, query_embedding, limit=32)
            docs = [_segment_ref(s) for s in candidates]
            yield {"event": "agent_action", "data": "Агент: ранжирую найденные фрагменты reranker-моделью"}
            ranking = await self.deps.reranker.rerank(question, docs)
            ranked_docs = [docs[i] for i in ranking[:12]] if ranking else docs[:12]
            context = "\n".join(ranked_docs)
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Вопрос пользователя:\n"
                        f"{question}\n\n"
                        "Релевантные фрагменты стенограммы с временными интервалами:\n"
                        f"{context}\n\n"
                        "Ответь по-русски. Если информации нет в контексте, честно скажи, что в диалоге это не найдено. "
                        "Когда уместно, ссылайся на временные интервалы."
                    ),
                },
            ]
            yield {"event": "agent_action", "data": "Агент: формирую ответ через openai/gpt-oss-120b"}
            final_parts: list[str] = []
            async for token in self.deps.chat.stream(messages):
                final_parts.append(token)
                yield {"event": "token", "data": token}
            yield {"event": "final", "data": "".join(final_parts)}
            return

        # Fallback for tests/dev if LLM dependencies are not injected.
        context = " ".join(_segment_ref(s) for s in (segments or [])[:20])
        answer = context[:1000] or "В стенограмме нет информации для ответа."
        for token in answer.split():
            yield {"event": "token", "data": token + " "}
        yield {"event": "final", "data": answer}


def sse(event):
    return f"event: {event['event']}\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"
