from pydantic import BaseModel

class RAGRequest(BaseModel):
    question: str
