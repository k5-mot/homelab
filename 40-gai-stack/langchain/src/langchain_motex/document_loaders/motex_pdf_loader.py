#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from pathlib import Path
from typing import Iterator, Union

from dotenv import load_dotenv
from langchain_community.document_loaders import (
    PDFMinerLoader,
    PDFPlumberLoader,
    PyPDFium2Loader,
    PyPDFLoader,
    UnstructuredPDFLoader,
)
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

from langchain_motex.document_loaders.docling_loader import DoclingLoader
from langchain_motex.document_loaders.markitdown_loader import MarkItDownLoader

UNSTRUCTURED_API_URL = os.getenv("UNSTRUCTURED_API_URL", "http://homelab-unstructured:9500/general/v0/general")
UNSTRUCTURED_API_KEY = os.getenv("UNSTRUCTURED_API_KEY", "unstructured")

class MotexPDFLoader(BaseLoader):
    file_path: Union[str, Path]

    def __init__(
        self,
        file_path: Union[str, Path],
    ):
        self.file_path = file_path

    def lazy_load(self) -> Iterator[Document]:
        """Load"""
        ext = os.path.splitext(self.file_path)[1]
        if ext != ".pdf":
            return []

        # Load PDF as Document
        loaders = [
            DoclingLoader(file_path=self.file_path),
            MarkItDownLoader(file_path=self.file_path),
            PDFPlumberLoader(file_path=self.file_path),
            PyPDFium2Loader(file_path=self.file_path),
            PDFMinerLoader(file_path=self.file_path),
            PyPDFLoader(file_path=self.file_path),
            UnstructuredPDFLoader(
                file_path=self.file_path,
                partition_via_api=True,
                url=UNSTRUCTURED_API_URL,
                api_key=UNSTRUCTURED_API_KEY,
                strategy="fast",
                chunking_strategy="none"
            ),
        ]
        for loader in loaders:
            try:
                doc = loader.load()
            except Exception as ex:
                print(f"Error loading {self.file_path}: {ex}")
                continue
            else:
                break

        return doc


if __name__ == "__main__":
    if os.path.isfile(".env"):
        load_dotenv()

    FILES = [
        "../docs/sample/nri.pdf",
    ]
    for file in FILES:
        loader = MotexPDFLoader(file)
        docs = loader.load()
        print(docs)
        for doc in docs:
            print(doc)
            print(doc.page_content)
