#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from pathlib import Path
from typing import Iterator, Union

from dotenv import load_dotenv
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from markitdown import MarkItDown


class MarkItDownLoader(BaseLoader):
    file_path: Union[str, Path]

    def __init__(
        self,
        file_path: Union[str, Path],
    ):
        """Initialize with file path."""
        self.file_path = file_path
        if "~" in self.file_path:
            self.file_path = os.path.expanduser(self.file_path)
        if not os.path.isfile(self.file_path):
            raise ValueError(f"Not found {self.file_path}.")


    def lazy_load(self) -> Iterator[Document]:
        """Load given path as single page."""
        try:
            loader = MarkItDown()
            result = loader.convert(self.file_path)
            yield Document(page_content=result.text_content)
        except Exception as ex:
            print(f"Error loading {self.file_path}: {ex}")



if __name__ == "__main__":
    if os.path.isfile(".env"):
        load_dotenv()

    FILES = [
        "../docs/sample/nri.pdf",
        "../docs/sample/melco.html",
        "../docs/sample/mitsuico.docx",
        # "../docs/sample2/ntt.md",
    ]
    for file in FILES:
        loader = MarkItDownLoader(file)
        docs = loader.load()
        for doc in docs:
            print(doc.page_content)
