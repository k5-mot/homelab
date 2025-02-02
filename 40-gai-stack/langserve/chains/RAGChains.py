import logging.config
import os, re, glob
from operator import itemgetter
from typing import List, Dict, Any
from dotenv import load_dotenv
import ollama, elasticsearch, chromadb
from langchain.globals import set_debug, set_verbose
from langchain_core.documents import Document
from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnablePassthrough,
    RunnableParallel,
    RunnableConfig,
)
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


set_debug(False)
set_verbose(False)


BASE_MODEL_NAME = "elyza3:8b"
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://homelab-ollama:11434")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-09-01-preview")
CHROMA_API_URL = os.getenv("CHROMA_API_URL", "http://homelab-chroma:8000")
ELASTICSEARCH_API_URL = os.getenv(
    "ELASTICSEARCH_API_URL", "http://homelab-elasticsearch:9200"
)

# Prompt template
SYSTEM_TEMPLATE = """
あなたは日本人で日本語で質問に回答する親切なassistantです。
取得されたcontextの情報の一部に基づいてなるべく詳細に質問に回答してください。
最大4つの文章で根拠を以て回答してください。
なるべく人のような口調で回答をするようにしてください。
もし回答を知らない場合は単に知らないと回答してください。
"""
HUMAN_TEMPLATE = """
Question: {question}
Context: {context}
Answer:
"""


def format_docs(docs: List[Document]) -> str:
    """Union contexts."""
    return "\n\n".join(doc.page_content for doc in docs)


def format_docs_chainlit(docs: List[Document]) -> List[Dict[str, str]]:
    """Union contexts."""
    contexts = []
    for doc in docs:
        file_path = os.path.abspath(doc.metadata["file_path"])

        # Check if exists in elements
        exist_context = None
        for context in contexts:
            if file_path == context["file_path"]:
                exist_context = context

        # Add context to element
        if exist_context is None:
            # Create new element
            content = "- Score: {}\n\n{}".format(
                str(doc.metadata["relevance_score"]), doc.page_content
            )
            contexts.append(
                {
                    "file_path": file_path,
                    "content": content,
                }
            )
        else:
            content = "\n- - - - - -\n- Score: {}\n\n{}".format(
                str(doc.metadata["relevance_score"]), doc.page_content
            )
            exist_context["content"] += content

    return contexts


def get_rag_chain(collection_name: str) -> Dict[str, Runnable | Dict[str, Any]]:

    # Setup Prompts
    system_prompt = SystemMessagePromptTemplate.from_template(SYSTEM_TEMPLATE)
    human_prompt = HumanMessagePromptTemplate.from_template(HUMAN_TEMPLATE)
    prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])

    # Setup LLM
    llm = ChatOllama(base_url=OLLAMA_API_URL, model=BASE_MODEL_NAME)
    # llm = AzureOpenAI(
    #     # model=BASE_MODEL_NAME,
    #     azure_endpoint=AZURE_OPENAI_ENDPOINT,
    #     api_key=AZURE_OPENAI_API_KEY,
    #     api_version=AZURE_OPENAI_API_VERSION,
    # )

    # Setup Output Parser
    parser = StrOutputParser()

    # Setup Dense/Sparse Vector Store
    embeddings = OllamaEmbeddings(
        base_url=OLLAMA_API_URL, model="nomic-embed-text:latest"
    )
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

    # Create Reranking and Ensemble Retriever
    dense_retriever = dense_vectorstore.as_retriever(search_kwargs={"k": 5})
    sparse_retriever = sparse_vectorstore.as_retriever(search_kwargs={"k": 5})
    ensemble_retriever = EnsembleRetriever(
        retrievers=[dense_retriever, sparse_retriever], weights=[0.5, 0.5]
    )
    compressor = FlashrankRerank(score_threshold=0.9, top_n=2)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, base_retriever=ensemble_retriever
    )

    # Setup RAG Chain
    chain = (
        RunnableParallel(
            {
                "question": itemgetter("question"),
                "context": itemgetter("question") | compression_retriever,
            }
        )
        | RunnableParallel(
            {
                "question": itemgetter("question"),
                "context": itemgetter("context"),
                "prompt": RunnableParallel(
                    {
                        "question": itemgetter("question"),
                        "context": RunnableLambda(
                            lambda inputs: format_docs(inputs["context"])
                        ),
                    }
                )
                | prompt,
            }
        )
        | RunnableParallel(
            {
                "answer": itemgetter("prompt") | llm | parser,
                "question": itemgetter("question"),
                "context": RunnableLambda(
                    lambda inputs: format_docs_chainlit(inputs["context"])
                ),
                "prompt": itemgetter("prompt"),
            }
        ).with_types(
            input_type=Dict[str, str], output_type=Dict[str, str | List[Dict[str, str]]]
        )
    )
    provider = "Ollama"  # str(type(llm))
    docs_dir = f"/docs/{collection_name}"
    path = re.sub(
        r"[ :\.\-/]", "_", f"{provider}_{BASE_MODEL_NAME}_rag_{docs_dir}"
    ).lower()
    content = ""
    if os.path.isfile(f"{docs_dir}/CONTENT.txt"):
        with open(f"{docs_dir}/CONTENT.txt", encoding="utf-8") as f:
            for line in f.readlines():
                content += line + "\n"

    metadata = {
        "title": f"RAG - {docs_dir}",
        "provider": provider,
        "base_model": BASE_MODEL_NAME,
        "collection": collection_name,
        "docs_dir": docs_dir,
        "path": path,
        "content": f"- **Provider**: {provider}\n- **Model**: {BASE_MODEL_NAME}\n- **Collection**: {collection_name}\n- **Directory**: {docs_dir}\n- **Content**: {content}",
    }
    return {"chain": chain, "metadata": metadata}


def get_rag_chains() -> List[Dict[str, Runnable | Dict[str, Any]]]:
    """Get RAG chains."""

    # Chroma client
    try:
        client_chroma = chromadb.HttpClient(
            host=CHROMA_API_URL,
            settings=chromadb.config.Settings(anonymized_telemetry=False),
        )
        collections = [
            collection.name for collection in client_chroma.list_collections()
        ]
    except Exception as ex:
        collections = []

    # Elasticsearch client
    try:
        client_es = elasticsearch.Elasticsearch(hosts=ELASTICSEARCH_API_URL)
        indices = [
            index["index"] for index in client_es.cat.indices(index="*", format="json")
        ]
    except Exception as ex:
        indices = []

    # Extract commons
    commons = set(collections) & set(indices)
    chains = [get_rag_chain(common) for common in commons]
    return chains


if __name__ == "__main__":
    chains = get_rag_chains()
    print("RAGChains")
    for chain_with_metadata in chains:
        chain = chain_with_metadata["chain"]
        metadata = chain_with_metadata["metadata"]
        print(metadata["path"])

    sample_chains = [
        chain for chain in chains if chain["metadata"]["collection"] == "sample"
    ]
    if len(sample_chains) <= 0:
        exit(-1)
    sample_chain = sample_chains[0]["chain"]
    res = sample_chain.invoke(input={"question": "MELCOとはどの企業の略称ですか?"})
    # print(res)
