from types import SimpleNamespace
from uuid import uuid4

import pytest

from src.infrastructure.agents.graph import AgentDependencies, TranscriptAgentGraph


class FakeRepo:
    async def vector_search_segments(self, job_id, embedding, limit=24):
        return [
            SimpleNamespace(
                start_seconds=0,
                end_seconds=12,
                speaker_name=None,
                speaker_label="SPEAKER_01",
                text="Иванов предложил срок до пятницы.",
            )
        ]


class FakeEmbedder:
    async def embed(self, texts):
        return [[0.1, 0.2, 0.3] for _ in texts]


class FakeReranker:
    async def rerank(self, query, docs):
        return [0]


class FakeChat:
    async def stream(self, messages):
        yield "Иванов "
        yield "предложил срок [0.0–12.0]."


@pytest.mark.asyncio
async def test_agent_graph_uses_rag_before_tokens():
    deps = AgentDependencies(FakeRepo(), FakeEmbedder(), FakeReranker(), FakeChat())
    events = [event async for event in TranscriptAgentGraph(deps).stream(uuid4(), "Что сказал Иванов?")]
    names = [event["event"] for event in events]
    assert names.index("agent_action") < names.index("token")
    assert any("PGVector" in event.get("data", "") for event in events)
    assert events[-1]["event"] == "final"
