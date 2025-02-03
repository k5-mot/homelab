import os

from dotenv import load_dotenv
from langchain_core.documents import Document

from langchain_motex.document_loaders import MotexDirLoader


class TestMotexDirLoader:

  def test__load(self):

    if os.path.isfile(".env"):
        load_dotenv()

    DIRPATH = os.path.abspath("../docs/sample")
    loader = MotexDirLoader(DIRPATH)
    docs = loader.load()
    for doc in docs:
        print(doc.page_content)
        assert type(doc) is Document
