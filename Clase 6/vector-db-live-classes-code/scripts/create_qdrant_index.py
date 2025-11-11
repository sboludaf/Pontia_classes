import sys 
from dotenv import load_dotenv

sys.path.append('.')
load_dotenv()

from qdrant_client import QdrantClient
from langchain_community.document_loaders import PyPDFDirectoryLoader
from qdrant_client.models import VectorParams, Distance, PointStruct
from src.services.embeddings import embeddings_google_genai
import os 
import time 

data_path = 'data/optimized_chunks'
loader = PyPDFDirectoryLoader(data_path)
documents = loader.load()

for doc in documents:
    source_path = doc.metadata.get('source','')
    file_name = os.path.basename(source_path)
    source_name = os.path.splitext(file_name)[0]
    doc.metadata['source'] = source_name

collection_name = "qdrantclient_index"
qdrant_url = "http://localhost:6333"

client = QdrantClient(url=qdrant_url)

try:
    client.get_collection(collection_name)
    client.delete_collection(collection_name)
except:
    pass 

client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=3072,distance=Distance.COSINE),
)


to_load_documents = [] 
for idx, document in enumerate(documents):
    embeddings_content = embeddings_google_genai.models.embed_content(
        model="gemini-embedding-001",
        contents=document.page_content
    )

    to_load_documents.append(
        PointStruct(
            id=idx,
            vector=embeddings_content.embeddings[0].values,
            payload={'content': document.page_content,"source": document.metadata['source'] }
        )
    )
    time.sleep(3)


operation_info = client.upsert(
    collection_name=collection_name,
    wait=True,
    points=to_load_documents
)

print("Index Created")