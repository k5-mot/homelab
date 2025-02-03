import os

from dotenv import load_dotenv
from langchain_core.documents import Document

from langchain_motex.document_loaders.motex_word_loader import MotexWordLoader


class TestMotexWordLoader:

  def test__load(self):

    if os.path.isfile(".env"):
        load_dotenv()

    FILES = [
        "../docs/sample/mitsuico.docx",
    ]
    for file in FILES:
        loader = MotexWordLoader(file)
        docs = loader.load()
        for doc in docs:
            print(doc.page_content)
        assert type(doc) is Document
