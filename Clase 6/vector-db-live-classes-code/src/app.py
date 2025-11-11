from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

# Add routers
from api.router_clients import router as clients_rag_router
from api.router_langchain import router as langchain_rag_router
from api.router_llamaindex import router as llama_index_rag_router


logger = logging.getLogger('uvicorn')
# Placeholder for lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML models and other resources
    logger.info("Starting up...")
    yield
    # Clean up the ML models and other resources
    logger.info("Shutting down...")

app = FastAPI(
    title="RAG and Semantic Search API",
    description="An API for RAG and Semantic Search with LangChain, LlamaIndex, and direct clients.",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the RAG and Semantic Search API"}



app.include_router(langchain_rag_router, prefix="/langchain", tags=["LangChain System"])
app.include_router(llama_index_rag_router, prefix="/llama_index", tags=["LlamaIndex System"])
app.include_router(clients_rag_router, prefix="/clients", tags=["Clients System"])
