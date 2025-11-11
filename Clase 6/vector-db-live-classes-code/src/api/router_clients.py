from fastapi import APIRouter

from src.api.schema import RAGRequest
from src.processes.client_process.process import get_answer
from src.services.embeddings import embeddings_google_genai
from src.services.vector_store import async_qdrant_client

router = APIRouter()

@router.post("/rag")
async def rag_endpoint(request: RAGRequest):
    """
    Endpoint to interact with the RAG system.
    """
    response = await get_answer(request.question)
    return response


@router.post("/search")
async def search(query: str):
    embeddings = await embeddings_google_genai.aio.models.embed_content(
        model="gemini-embedding-001",
        contents=query
    )

    found_docs = await async_qdrant_client.search(
        collection_name='qdrantclient_index',
        query_vector=embeddings.embeddings[0].values,
        with_payload=True,
        limit=5
    )

    return found_docs