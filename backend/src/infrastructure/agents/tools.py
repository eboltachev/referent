from pydantic import BaseModel
class RetrieveInput(BaseModel): job_id: str; query: str
class TimeInput(BaseModel): seconds: float
class CalculatorInput(BaseModel): expression: str
def select_tools(question: str) -> list[str]:
    q=question.lower(); tools=['pgvector_retriever','reranker']
    if any(w in q for w in ['сколько','числ','how many']): tools.append('calculator')
    if any(w in q for w in ['минут','время','срок','time']): tools.append('time_tool')
    if any(w in q for w in ['кто','спикер','иванов']): tools.append('speaker_resolver')
    return tools
