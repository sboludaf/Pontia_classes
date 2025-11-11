import sys 
from dotenv import load_dotenv

sys.path.append('.')
load_dotenv()

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from src.services.embeddings import embeddings_model_llama_index
import os 
import time

data_path = 'data/optimized_chunks'
loader = SimpleDirectoryReader(data_path)
documents = loader.load_data()

for doc in documents:
    source_path = doc.metadata.get('source','')
    file_name = os.path.basename(source_path)
    source_name = os.path.splitext(file_name)[0]
    doc.metadata['source'] = source_name

collection_name = "llamaindex_index"
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

vector_store = QdrantVectorStore(
    client=client, 
    collection_name= collection_name,
    batch_size=1
)

storage_context = StorageContext.from_defaults(vector_store=vector_store)

#index = VectorStoreIndex.from_documents(
#    documents,
#    storage_context=storage_context,
#    embed_model=embeddings_model_llama_index,
#    show_progress=True
#)


vector_store = VectorStoreIndex(
    nodes=[],
    storage_context=storage_context,
    embed_model=embeddings_model_llama_index
)
for document in documents:
    document.metadata['source'] = document.metadata['file_name'].split('.pd')[0]
    
for document in documents:
    vector_store.insert(document)
    time.sleep(2)