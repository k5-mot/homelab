#!/usr/bin/env python
# -*- coding: utf-8 -*-

from langchain_motex.document_loaders.docling_loader import DoclingLoader
from langchain_motex.document_loaders.markitdown_loader import MarkItDownLoader
from langchain_motex.document_loaders.motex_dir_loader import MotexDirLoader
from langchain_motex.document_loaders.motex_excel_loader import MotexExcelLoader
from langchain_motex.document_loaders.motex_file_loader import MotexFileLoader
from langchain_motex.document_loaders.motex_misc_loader import MotexMiscLoader
from langchain_motex.document_loaders.motex_pdf_loader import MotexPDFLoader
from langchain_motex.document_loaders.motex_powerpoint_loader import (
    MotexPowerPointLoader,
)
from langchain_motex.document_loaders.motex_word_loader import MotexWordLoader

__all__ = [
    "DoclingLoader",
    "MarkItDownLoader",
    "MotexDirLoader",
    "MotexExcelLoader",
    "MotexFileLoader",
    "MotexMiscLoader",
    "MotexPDFLoader",
    "MotexPowerPointLoader",
    "MotexWordLoader"
]
