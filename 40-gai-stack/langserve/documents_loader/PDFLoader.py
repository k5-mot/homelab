import csv
from io import TextIOWrapper
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence, Union

from langchain_core.documents import Document

from langchain_community.document_loaders.base import BaseLoader
from langchain_community.document_loaders.helpers import detect_file_encodings
from langchain_community.document_loaders.unstructured import (
    UnstructuredFileLoader,
    validate_unstructured_version,
)
import glob
import mimetypes
import os
import re
import statistics
from typing import List
import chromadb
from elasticsearch import Elasticsearch
from langchain.text_splitter import (
    HTMLHeaderTextSplitter,
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
    SpacyTextSplitter,
)
from langchain_community.document_loaders import (  # UnstructuredAPIFileLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredPDFLoader,
    PDFPlumberLoader,
    PyPDFium2Loader,
    PDFMinerLoader,
    Docx2txtLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader,
    UnstructuredExcelLoader,
)
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_unstructured import UnstructuredLoader
from langchain_ollama import OllamaEmbeddings
from langchain_elasticsearch import ElasticsearchStore
from langchain.globals import set_debug, set_verbose


class PDFLoader(BaseLoader):

    def __init__(
        self,
        file_path: Union[str, Path],
    ):
        self.file_path = file_path

    def lazy_load(self) -> Iterator[Document]:
        ext = os.path.splitext(file_path)[1]
        if ext != ".pdf":
            return []

        # Load PDF as Document
        loaders = [
            PDFPlumberLoader(file_path=file_path),
            PyPDFium2Loader(file_path=file_path),
            PDFMinerLoader(file_path=file_path),
            PyPDFLoader(file_path=file_path),
            UnstructuredPDFLoader(
                file_path=file_path,
                max_characters=1000000,
                partition_via_api=True,
                url=UNSTRUCTURED_API_URL,
                api_key=UNSTRUCTURED_API_KEY,
            ),
        ]
        for loader in loaders:
            try:
                doc = loader.load()
            except Exception as ex:
                print(f"Error loading {file_path}: {ex}")
                continue
            else:
                break
        try:
            with open(self.file_path, newline="", encoding=self.encoding) as csvfile:
                yield from self.__read_file(csvfile)
        except UnicodeDecodeError as e:
            if self.autodetect_encoding:
                detected_encodings = detect_file_encodings(self.file_path)
                for encoding in detected_encodings:
                    try:
                        with open(
                            self.file_path, newline="", encoding=encoding.encoding
                        ) as csvfile:
                            yield from self.__read_file(csvfile)
                            break
                    except UnicodeDecodeError:
                        continue
            else:
                raise RuntimeError(f"Error loading {self.file_path}") from e
        except Exception as e:
            raise RuntimeError(f"Error loading {self.file_path}") from e


    def __read_file(self, csvfile: TextIOWrapper) -> Iterator[Document]:
        csv_reader = csv.DictReader(csvfile, **self.csv_args)
        for i, row in enumerate(csv_reader):
            try:
                source = (
                    row[self.source_column]
                    if self.source_column is not None
                    else str(self.file_path)
                )
            except KeyError:
                raise ValueError(
                    f"Source column '{self.source_column}' not found in CSV file."
                )
            content = "\n".join(
                f"""{k.strip() if k is not None else k}: {v.strip()
                if isinstance(v, str) else ','.join(map(str.strip, v))
                if isinstance(v, list) else v}"""
                for k, v in row.items()
                if (
                    k in self.content_columns
                    if self.content_columns
                    else k not in self.metadata_columns
                )
            )
            metadata = {"source": source, "row": i}
            for col in self.metadata_columns:
                try:
                    metadata[col] = row[col]
                except KeyError:
                    raise ValueError(f"Metadata column '{col}' not found in CSV file.")
            yield Document(page_content=content, metadata=metadata)
