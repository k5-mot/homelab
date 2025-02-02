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
        self.file_path = file_path

    def lazy_load(self) -> Iterator[Document]:
        """Load"""
        try:
            md = MarkItDown()
            result = md.convert(self.file_path)
            docs = [Document(page_content=result.text_content)]
        except Exception as ex:
            docs = []
            print(f"{ex}")

        for doc in docs:
            yield doc


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
