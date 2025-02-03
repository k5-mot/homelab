import os

from dotenv import load_dotenv
from langchain_core.documents import Document

from langchain_motex.document_loaders import MotexPDFLoader


class TestMotexPDFLoader:

  def test__load(self):

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
            assert type(doc) is Document
