import glob
import mimetypes
import os
import re
import shutil
import statistics
import sys
from typing import List

import chromadb
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.retrievers import ContextualCompressionRetriever, EnsembleRetriever
from langchain.schema import StrOutputParser
from langchain.text_splitter import (
    HTMLHeaderTextSplitter,
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
    SpacyTextSplitter,
)
from langchain_anthropic import ChatAnthropic
from langchain_chroma import Chroma
from langchain_community.chat_models import ChatOllama
from langchain_community.document_compressors import FlashrankRerank
from langchain_community.document_loaders import (  # UnstructuredAPIFileLoader,
    PyMuPDFLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredPDFLoader,
)

# from langchain_community.embeddings import OllamaEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_unstructured import UnstructuredLoader


OLLAMA_API_URL = "http://homelab-ollama:11434"
CHROMA_API_URL = "http://homelab-chroma:8000"
UNSTRUCTURED_API_URL = "http://homelab-unstructured:8000/general/v0/general"
UNSTRUCTURED_API_KEY = "unstructured"
SEPARATORS = [
    "\n\n",
    "\n",
    " ",
    ".",
    ",",
    "\u200b",  # Zero-width space
    "\uff0c",  # Fullwidth comma
    "\u3001",  # Ideographic comma
    "\uff0e",  # Fullwidth full stop
    "\u3002",  # Ideographic full stop
    "",
]


def rearrange_metadata(documents: List[Document]) -> List[Document]:
    """Rearrange metadata for vector stores"""
    for document in documents:
        # Remove unsupported datatypes by vector stores
        for k, v in document.metadata.items():
            metatype = type(v)
            if metatype in (str, int, float, bool):
                continue
            elif metatype in (list, tuple):
                document.metadata[k] = document.metadata[k][0]
            else:
                document.metadata.pop(k)
    return documents


def get_filetype(filepath: str) -> str:
    mimetypes.add_type("text/x-toml", ".toml")
    mimetypes.add_type("text/x-yaml", ".yml")
    mimetypes.add_type("text/x-yaml", ".yaml")
    mimetypes.add_type("text/x-sh", ".gitignore")
    guess_type = mimetypes.guess_type(filepath)[0] or ""
    mime_type = re.sub("^[a-z]+/", "", guess_type)
    mime_type = re.sub("^x-", "", mime_type)
    mime_type = re.sub("^plain", "text", mime_type)
    return mime_type.lower()


def add_fileinfo_to_metadata(
    documents: List[Document], file_path: str
) -> List[Document]:
    """Set file info to metadata for traceability"""
    abspath = os.path.abspath(file_path)
    basename = os.path.basename(file_path)
    for document in documents:
        document.metadata["file_path"] = abspath
        document.metadata["filename"] = basename
        document.metadata["file_type"] = get_filetype(basename)
    return documents


def load_and_split_pdf(file_path: str) -> List[Document]:
    ext = os.path.splitext(file_path)[1]
    if ext != ".pdf":
        return []

    # Load PDF as Document
    loaders = [
        PyMuPDFLoader(file_path=file_path),
        PyPDFLoader(file_path=file_path),
        UnstructuredPDFLoader(file_path=file_path),
    ]
    for loader in loaders:
        try:
            doc = loader.load()
        except Exception as ex:
            print(f"Error loading {file_path}: {ex}")
            continue
        else:
            break

    # Split Document
    text_splitter = SpacyTextSplitter(chunk_size=500, pipeline="ja_core_news_lg")
    splitted_doc = text_splitter.split_documents(doc)
    return splitted_doc


def load_and_split_markdown(file_path: str) -> List[Document]:
    # Load PDF as Document
    loader = TextLoader(file_path=file_path)
    try:
        doc = loader.load()
    except Exception as ex:
        print(f"Error loading {file_path}: {ex}")
        return []

    # Split Document
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ("####", "Header 4"),
    ]
    text_splitter_md = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on, return_each_line=True
    )
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=0,
        length_function=len,
        is_separator_regex=False,
        separators=SEPARATORS,
    )
    splitted_docs: List[Document] = []
    for frag in doc:
        splitted_doc = text_splitter_md.split_text(
            frag.page_content.replace("\n\n", "\n")
        )
        splitted_doc = text_splitter.split_documents(splitted_doc)
        splitted_docs.extend(splitted_doc)
    return splitted_doc


def load_and_split_html(file_path: str) -> List[Document]:
    # Load PDF as Document
    loader = TextLoader(file_path=file_path)
    try:
        doc = loader.load()
    except Exception as ex:
        print(f"Error loading {file_path}: {ex}")
        return []

    # Split Document
    headers_to_split_on = [
        ("h1", "Header 1"),
        ("h2", "Header 2"),
    ]
    text_splitter_html = HTMLHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
    )
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=0,
        length_function=len,
        is_separator_regex=False,
        separators=SEPARATORS,
    )
    splitted_docs: List[Document] = []
    for frag in doc:
        splitted_doc = text_splitter_html.split_text(
            frag.page_content.replace("\n\n", "\n")
        )
        splitted_doc = text_splitter.split_documents(splitted_doc)
        splitted_docs.extend(splitted_doc)
    return splitted_doc


def load_and_split_unknown(file_path: str) -> List[Document]:
    # Load PDF as Document
    # os.environ["UNSTRUCTURED_API_URL"] = UNSTRUCTURED_API_URL
    # os.environ["UNSTRUCTURED_API_KEY"] = UNSTRUCTURED_API_KEY
    loader = UnstructuredLoader(
        file_path=file_path,
        chunking_strategy="basic",
        max_characters=1000000,
        include_orig_elements=False,
        # partition_via_api=True,
        # url = UNSTRUCTURED_API_URL,
        # api_key = UNSTRUCTURED_API_KEY,
    )
    try:
        doc = loader.load()
    except Exception as ex:
        print(f"Error loading {file_path}: {ex}")
        return []

    # Split Document
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ("####", "Header 4"),
    ]
    text_splitter_md = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on, return_each_line=True
    )
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=0,
        length_function=len,
        is_separator_regex=False,
        separators=SEPARATORS,
    )
    splitted_docs: List[Document] = []
    for frag in doc:
        splitted_doc = text_splitter_md.split_text(
            frag.page_content.replace("\n\n", "\n")
        )
        splitted_doc = text_splitter.split_documents(splitted_doc)
        splitted_docs.extend(splitted_doc)
    return splitted_docs


def load_and_split_all(dir_path: str = "/workspace/docs") -> List[Document]:
    """Load various files."""
    # Get files from a specified directory
    file_paths = [
        os.path.abspath(file_path)
        for file_path in glob.glob(f"{dir_path}/**/*", recursive=True)
    ]

    # Convert various file format to plain text
    docs: List[Document] = []
    for file_path in file_paths:
        # Load and Split all files
        ext = os.path.splitext(file_path)[1]
        if ext == ".pdf":
            doc = load_and_split_pdf(file_path)
        elif ext == ".md":
            doc = load_and_split_markdown(file_path)
        elif ext == ".html":
            doc = load_and_split_html(file_path)
        else:
            doc = load_and_split_unknown(file_path)

        # Rearrrange metadatas
        doc = rearrange_metadata(doc)
        doc = add_fileinfo_to_metadata(doc, file_path)
        docs.extend(doc)
        print(f"Loaded {file_path}")
    return docs


def save_documents(docs: List[Document], save_dir: str = "./debug"):
    os.makedirs(save_dir, exist_ok=True)
    for doc in docs:
        filename = doc.metadata["filename"]
        with open(f"{save_dir}/{filename}.txt", mode="a") as f:
            f.write(doc.page_content)
            f.write("\n---\n")
    print(f"Saved Documents to {save_dir}")


def eval_documents(docs: List[Document]):
    docsizes = [len(doc.page_content) for doc in docs]
    print(f"Min: {min(docsizes)}")
    print(f"Max: {max(docsizes)}")
    print(f"Mean: {statistics.mean(docsizes)}")
    print(f"Std: {statistics.stdev(docsizes)}")
    print(f"Var: {statistics.variance(docsizes)}")


# Clear Vector store
try:
    client = chromadb.HttpClient(
        host=CHROMA_API_URL,
        settings=chromadb.config.Settings(anonymized_telemetry=False),
    )
    for collection in client.list_collections():
        client.delete_collection(name=collection.name)
except Exception as e:
    exit(1)

# Embedding model
embeddings = OllamaEmbeddings(base_url=OLLAMA_API_URL, model="nomic-embed-text:latest")

for rootdir in glob.glob("/workspace/docs/*/"):
    collection_name = re.sub("/$", "", rootdir)
    collection_name = os.path.basename(collection_name)

    # Documents loader
    documents = load_and_split_all(rootdir)
    # eval_documents(documents)
    # save_documents(documents, "./debug/fin")

    # Vector store
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        client=client,
    )
    vectorstore.add_documents(documents)


# document_1 = Document(
#     page_content="I had chocolate chip pancakes and scrambled eggs for breakfast this morning.",
#     metadata={"source": "tweet"},
#     id=1,
# )
# vectorstore.add_documents(documents=[document_1])