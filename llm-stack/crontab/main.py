import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.documents import Document

OLLAMA_API_URL = "http://homelab-ollama:11434"
CHROMA_API_URL = "http://homelab-chroma:8000"

# Embedding model
embeddings = OllamaEmbeddings(base_url=OLLAMA_API_URL, model="nomic-embed-text:latest")

# Vector Store
try:
    client = chromadb.HttpClient(
        host=CHROMA_API_URL,
        settings=Settings(anonymized_telemetry=False),
    )
    print("PING: " + str(client.heartbeat()))

    for collection in client.list_collections():
        print(collection)
        client.delete_collection(name=collection.name)
except Exception as e:
    exit(1)

vectorstore = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,
    client=client,
)

document_1 = Document(
    page_content="I had chocolate chip pancakes and scrambled eggs for breakfast this morning.",
    metadata={"source": "tweet"},
    id=1,
)
vectorstore.add_documents(documents=[document_1])
