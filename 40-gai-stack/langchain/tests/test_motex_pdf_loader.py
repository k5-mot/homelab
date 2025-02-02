import os

import pytest
from dotenv import load_dotenv

from langchain_motex.document_loaders.motex_pdf_loader import MotexPDFLoader


class TestMotexPDFLoader:

  def test__can_print_aaa(self):

    if os.path.isfile(".env"):
        load_dotenv()
    FILES = [
        "../docs/sample/nri.pdf",
    ]
    for file in FILES:
        loader = MotexPDFLoader(file)
        docs = loader.load()
        for doc in docs:
            print(doc.page_content)
