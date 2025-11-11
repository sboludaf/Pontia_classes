from google import genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

MODEL_NAME = 'models/gemini-embedding-001'

embeddings_google_genai = genai.Client()

embeddings_model_langchain = GoogleGenerativeAIEmbeddings(model=MODEL_NAME)

embeddings_model_llama_index = GoogleGenAIEmbedding(
    model_name=MODEL_NAME,
    embed_batch_size=1,
)