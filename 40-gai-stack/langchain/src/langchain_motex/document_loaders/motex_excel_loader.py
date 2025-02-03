#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from pathlib import Path
from typing import Iterator, Union

from dotenv import load_dotenv
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

from langchain_motex.document_loaders.docling_loader import DoclingLoader
from langchain_motex.document_loaders.markitdown_loader import MarkItDownLoader

UNSTRUCTURED_API_URL = os.getenv("UNSTRUCTURED_API_URL", "http://homelab-unstructured:9500/general/v0/general")
UNSTRUCTURED_API_KEY = os.getenv("UNSTRUCTURED_API_KEY", "unstructured")


class MotexExcelLoader(BaseLoader):

    file_path: Union[str, Path]

    def __init__(
        self,
        file_path: Union[str, Path],
    ):
        """Initialize with file path."""
        self.file_path = str(file_path)
        if "~" in self.file_path:
            self.file_path = os.path.expanduser(self.file_path)

        ext = os.path.splitext(self.file_path)[1]
        if not os.path.isfile(self.file_path):
            raise ValueError(f"Not found {self.file_path}.")
        elif ext not in [".xls", ".xlsx", ".xlsm"]:
            raise ValueError(f"Invalid file {self.file_path}.")


    def lazy_load(self) -> Iterator[Document]:
        """Load given path as single page."""
        # Setup document loaders
        loaders = [
            DoclingLoader(file_path=self.file_path),
            MarkItDownLoader(file_path=self.file_path),
            UnstructuredExcelLoader(
                file_path=self.file_path,
                partition_via_api=True,
                url=UNSTRUCTURED_API_URL,
                api_key=UNSTRUCTURED_API_KEY,
                strategy="fast",
                chunking_strategy="none"
            ),
        ]
        # Load documents
        for loader in loaders:
            try:
                docs = loader.load()
                for doc in docs:
                    yield doc
            except Exception as ex:
                print(f"Error loading {self.file_path}: {ex}")
                continue


if __name__ == "__main__":
    if os.path.isfile(".env"):
        load_dotenv()

    FILES = [
        "../docs/sample/nri.pdf",
    ]
    for file in FILES:
        loader = MotexExcelLoader(file)
        docs = loader.load()
        print(docs)
        for doc in docs:
            print(doc)
            print(doc.page_content)
