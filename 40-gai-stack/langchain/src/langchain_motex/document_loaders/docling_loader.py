#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from pathlib import Path
from typing import Iterator, Union

from docling.document_converter import DocumentConverter
from dotenv import load_dotenv
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document


class DoclingLoader(BaseLoader):
    file_path: Union[str, Path]

    def __init__(
        self,
        file_path: Union[str, Path],
    ):
        self.file_path = file_path

    def lazy_load(self) -> Iterator[Document]:
        """Load"""
        try:
            converter = DocumentConverter()
            result = converter.convert(self.file_path)
            md = result.document.export_to_markdown()
            docs = [Document(page_content=md)]
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
        loader = DoclingLoader(file)
        docs = loader.load()
        for doc in docs:
            print(doc.page_content)
