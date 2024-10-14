import glob
import mimetypes
import os
import re
import shutil
import statistics
import sys
from typing import List

import chainlit as cl
import chromadb
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.retrievers import ContextualCompressionRetriever, EnsembleRetriever
from langchain.schema import StrOutputParser
from langchain_core.documents import Document
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_community.document_compressors import FlashrankRerank
from langchain_anthropic import ChatAnthropic
from langchain_ollama.chat_models import ChatOllama
from langchain_openai import AzureOpenAI
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_elasticsearch import ElasticsearchStore


def format_docs(docs: List[Document]):
    """Union contexts."""
    return "\n\n".join(doc.page_content for doc in docs)


SYSTEM_TEMPLATE = "関連ドキュメントを元に、次の質問に答えてください。"
HUMAN_TEMPLATE = """
{question}

以下に、関連ドキュメントを示す。
{context}
"""
OLLAMA_API_URL = "http://homelab-ollama:11434"
CHROMA_API_URL = "http://homelab-chroma:8000"
ELASTICSEARCH_API_URL = "http://homelab-elasticsearch:9200"

# Prompt
system_prompt = SystemMessagePromptTemplate.from_template(SYSTEM_TEMPLATE)
human_prompt = HumanMessagePromptTemplate.from_template(HUMAN_TEMPLATE)
prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])

# LLM
# model = ChatAnthropic(temperature=1.0, model_name="claude-3-5-sonnet-20240620")
# model = AzureOpenAI(deployment_id="gpt-35-turbo", temperature=1.0)
model = ChatOllama(base_url=OLLAMA_API_URL, model="llama3.2:3b")

# Output parser
parser = StrOutputParser()

# Embedding model
embeddings = OllamaEmbeddings(base_url=OLLAMA_API_URL, model="nomic-embed-text:latest")

# Vector store
client_chroma = chromadb.HttpClient(
    host=CHROMA_API_URL,
    settings=chromadb.config.Settings(anonymized_telemetry=False),
)
dense_vectorstore = Chroma(
    collection_name="sample",
    embedding_function=embeddings,
    client=client_chroma,
)

# Vector store
sparse_vectorstore = ElasticsearchStore(
    index_name="sample",
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
rag_chain = (
    RunnablePassthrough(context=(lambda x: format_docs(x["context"])))
    | prompt
    | model
    | parser
)

# Rerank RAG chain
runnable = RunnableParallel(
    {"context": compression_retriever, "question": RunnablePassthrough()}
).assign(answer=rag_chain)


@cl.set_chat_profiles
async def set_chat_profiles():
    profiles = []
    for rootdir in glob.glob("/docs/*/"):
        profiles.append(
            cl.ChatProfile(
                name=f"{model.model} - {rootdir}",
                markdown_description=f"RAG chain of {model} in {rootdir}",
                # icon="https://picsum.photos/200",
            )
        )
    return profiles


@cl.on_chat_start
async def on_chat_start():
    user = cl.user_session.get("user")
    chat_profile: cl.ChatProfile = cl.user_session.get("chat_profile")
    await cl.Message(content=f"{chat_profile.name}").send()


@cl.on_message
async def on_message(message: cl.Message):
    reply = cl.Message(content="", elements=[])

    # Stream a reply message
    async for chunk in runnable.astream(message.content):
        # print(chunk)
        if "answer" in chunk.keys():
            await reply.stream_token(chunk["answer"])
        elif "context" in chunk.keys():
            contexts: List[Document] = chunk["context"]
        elif "question" in chunk.keys():
            question: str = chunk["question"]
    await reply.send()

    # Print intermediates
    print(question)
    for context in contexts:
        md = context.metadata

        if "id" in md.keys():
            printline = str(md["id"])
        else:
            printline = "?"

        printline += f"({md["file_path"]}): "

        if "relevance_score" in md.keys():
            printline += f"{md["relevance_score"]}"
        print(printline)
        # print(context.page_content)

    # Add documents referenced by RAG to a reply
    for context in contexts:
        # Skip added documents
        context_path = os.path.abspath(context.metadata["file_path"])

        # Add fragment to element
        el_flag = False
        for element in reply.elements:
            if context_path == element.name:
                element.content += "\n- - - - - -\n"
                element.content += context.page_content
                el_flag = True
                continue

        # Add document as element
        if el_flag:
            continue
        reply.elements.append(
            cl.Text(
                name=context_path,
                # language=context.metadata["file_type"],
                content=context.page_content,
                # path=context_path
            )
        )

    await reply.send()
