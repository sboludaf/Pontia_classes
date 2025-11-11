from fastapi import APIRouter

from src.api.schema import RAGRequest
from src.processes.langchain_chain.chain import rag_chain
from src.services.vector_store import qdrant_langchain

router = APIRouter()

@router.post("/rag")
async def rag_endpoint(request: RAGRequest):
    """
    Endpoint to interact with the RAG system.
    """
    result = await rag_chain.ainvoke({"question": request.question})
    return {
        "question": result["question"],
        "answer": result["answer"],
        "source": result["source"].selection if result.get('source') else None,
        "source_reason": result["source"].reason if result.get('source') else None
    }

@router.post("/search")
async def search(query: str):
    found_docs = qdrant_langchain.similarity_search(query, k=5)
    return found_docs