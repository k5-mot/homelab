#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from pathlib import Path
from typing import Iterator, Union

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from dotenv import load_dotenv
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document


class DoclingLoader(BaseLoader):
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
            # Setup document loaders
            pipeline_options = PdfPipelineOptions(
                images_scale=2.0,
                generate_page_images=True,
                generate_picture_images=True,
                generate_table_images=True
            )
            loader = DocumentConverter(
                 format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )

            # Load documents.
            result = loader.convert(self.file_path)
            content = result.document.export_to_markdown()
            yield Document(page_content=content)
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
        loader = DoclingLoader(file)
        docs = loader.load()
        for doc in docs:
            print(doc.page_content)
