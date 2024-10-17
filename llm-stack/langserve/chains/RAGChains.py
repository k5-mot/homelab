import os, re, glob
from typing import List
from dotenv import load_dotenv
import ollama
import elasticsearch
import chromadb
from langchain_core.documents import Document
from langchain_core.runnables import Runnable, RunnablePassthrough, RunnableParallel
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_ollama.chat_models import ChatOllama
from langchain_openai import AzureOpenAI, AzureOpenAIEmbeddings
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_elasticsearch import ElasticsearchStore
from langchain.retrievers import ContextualCompressionRetriever, EnsembleRetriever
from langchain_community.document_compressors import FlashrankRerank
from langchain.schema import StrOutputParser


OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://homelab-ollama:11434")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-09-01-preview")
CHROMA_API_URL = os.getenv("CHROMA_API_URL", "http://homelab-chroma:8000")
ELASTICSEARCH_API_URL = os.getenv(
    "ELASTICSEARCH_API_URL", "http://homelab-elasticsearch:9200"
)

# Prompt template
SYSTEM_TEMPLATE = "関連ドキュメントを元に、次の質問に答えてください。"
HUMAN_TEMPLATE = """
{question}

以下に、関連ドキュメントを示す。
{context}
"""


def format_docs(docs: List[Document]):
    """Union contexts."""
    return "\n\n".join(doc.page_content for doc in docs)


def getRAGChain(collection_name: str) -> Runnable:
    rootdir = f"/docs/{collection_name}"
    name = f"RAG Chain of {rootdir}"

    # Prompt
    system_prompt = SystemMessagePromptTemplate.from_template(SYSTEM_TEMPLATE)
    human_prompt = HumanMessagePromptTemplate.from_template(HUMAN_TEMPLATE)
    prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])

    # LLM
    model = ChatOllama(base_url=OLLAMA_API_URL, model="llama3.2:3b")
    # model = AzureOpenAI(
    #     # model="",
    #     azure_endpoint=AZURE_OPENAI_ENDPOINT,
    #     api_key=AZURE_OPENAI_API_KEY,
    #     api_version=AZURE_OPENAI_API_VERSION,
    # )

    # Embedding model
    embeddings = OllamaEmbeddings(
        base_url=OLLAMA_API_URL, model="nomic-embed-text:latest"
    )

    # Output parser
    parser = StrOutputParser()

    # Vector store
    dense_vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        client=chromadb.HttpClient(
            host=CHROMA_API_URL,
            settings=chromadb.config.Settings(anonymized_telemetry=False),
        ),
    )
    sparse_vectorstore = ElasticsearchStore(
        index_name=collection_name,
        embedding=embeddings,
        es_url=ELASTICSEARCH_API_URL,
        strategy=ElasticsearchStore.BM25RetrievalStrategy(),
    )

    # Dense Retriever
    dense_retriever = dense_vectorstore.as_retriever(search_kwargs={"k": 5})

    # Sparse Retriever
    sparse_retriever = sparse_vectorstore.as_retriever(search_kwargs={"k": 5})

    # Ensemble Retriever
    ensemble_retriever = EnsembleRetriever(
        retrievers=[dense_retriever, sparse_retriever], weights=[0.5, 0.5]
    )

    # Reranker
    compressor = FlashrankRerank(score_threshold=0.90, top_n=2)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, base_retriever=ensemble_retriever
    )

    # RAG chain
    chain_noinput = (
        RunnablePassthrough(context=(lambda x: format_docs(x["context"])))
        | prompt
        | model
        | parser
    )

    # Rerank RAG chain
    chain = RunnableParallel(
        {"context": compression_retriever, "question": RunnablePassthrough()}
    ).assign(answer=chain_noinput)
    chain.name = f"rag_{collection_name}"
    return chain


def getRAGChains() -> List[Runnable]:
    # Chroma client
    client_chroma = chromadb.HttpClient(
        host=CHROMA_API_URL,
        settings=chromadb.config.Settings(anonymized_telemetry=False),
    )
    collections = [collection.name for collection in client_chroma.list_collections()]

    # Elasticsearch client
    client_es = elasticsearch.Elasticsearch(hosts=ELASTICSEARCH_API_URL)
    indices = [
        index["index"] for index in client_es.cat.indices(index="*", format="json")
    ]

    # Union two retrievers
    union = set(collections) & set(indices)
    chains = [getRAGChain(collection) for collection in union]
    return chains


if __name__ == "__main__":
    chains = getRAGChains()
    print(chains)
    print(len(chains))
