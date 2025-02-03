#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob
import os
from pathlib import Path
from typing import Iterator, Union

from dotenv import load_dotenv
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

from langchain_motex.document_loaders.motex_file_loader import MotexFileLoader

UNSTRUCTURED_API_URL = os.getenv("UNSTRUCTURED_API_URL", "http://homelab-unstructured:9500/general/v0/general")
UNSTRUCTURED_API_KEY = os.getenv("UNSTRUCTURED_API_KEY", "unstructured")

def rearrange_metadata(doc: Document) -> Document:
    """Rearrange metadata for vector stores"""
    # Remove unsupported datatypes by vector stores
    for k, v in doc.metadata.items():
        metatype = type(v)
        if metatype in (str, int, float, bool):
            continue
        elif metatype in (list, tuple):
            doc.metadata[k] = doc.metadata[k][0]
        else:
            doc.metadata.pop(k)
    return doc


class MotexDirLoader(BaseLoader):

    dir_path: Union[str, Path]

    def __init__(
        self,
        dir_path: str = "/workspace/docs",
    ):
        """Initialize with directory path."""
        # Get files from a specified directory
        self.dir_path = str(dir_path)
        if "~" in self.dir_path:
            self.dir_path = os.path.expanduser(self.dir_path)

        if not os.path.isdir(self.dir_path):
            raise ValueError(f"Not found {self.dir_path}.")


    def lazy_load(self) -> Iterator[Document]:
        """Load given path as single page."""

        file_paths = [
            os.path.abspath(file_path)
            for file_path in glob.glob(f"{self.dir_path}/**/*", recursive=True)
        ]

        for file_path in file_paths:
            try:
                loader = MotexFileLoader(file_path)
                docs = loader.load()
                for doc in docs:
                    doc = rearrange_metadata(doc)
                    doc.metadata["file_path"] = os.path.abspath(file_path)
                    doc.metadata["filename"] = os.path.basename(file_path)
                    yield doc
            except Exception as ex:
                print(f"Error loading {file_path}: {ex}")


if __name__ == "__main__":
    if os.path.isfile(".env"):
        load_dotenv()

    FILES = [
        "../docs/sample/nri.pdf",
    ]
    for file in FILES:
        loader = MotexFileLoader(file)
        docs = loader.load()
        print(docs)
        for doc in docs:
            print(doc)
            print(doc.page_content)
