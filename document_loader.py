from abc import ABC, abstractmethod
from logging import getLogger
from typing import Optional

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from llama_parse import LlamaParse

from config import config

logger = getLogger(__name__)


class DocumentLoader(ABC):
    def __init__(self, file_path: str):
        self.file_path = file_path

    @abstractmethod
    def load(self) -> Optional[list[Document]]:
        pass

    def get_file_name(self) -> str:
        return self.file_path.split('/')[-1].split('.')[0]

    def split_documents(self, documents: list[Document]) -> list[Document]:
        logger.info(f"Splitting {len(documents)} documents")
        for i, doc in enumerate(documents):
            doc.metadata['page'] = str(i)
            doc.metadata['file_path'] = self.file_path

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=5000,
            chunk_overlap=500,
            length_function=len,
            is_separator_regex=True
        )
        docs = text_splitter.split_documents(documents)

        for i, doc in enumerate(docs):
            doc.metadata['chunk'] = str(i)
            doc.metadata['id'] = f"{doc.metadata['file_path']}:{doc.metadata['page']}:{doc.metadata['chunk']}"

        logger.info(f"Split into {len(docs)} chunks")

        return docs


class LlamaLoader(DocumentLoader):
    def load(self) -> Optional[list[Document]]:
        try:
            parser = LlamaParse(
                api_key=config.LLAMA_API_KEY,
                result_type="markdown",
                verbose=True,
                language="en",
            )
            documents = parser.load_data(self.file_path)

            langchain_documents = []

            for doc in documents:
                langchain_documents.append(doc.to_langchain_format())

            return langchain_documents
        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            return None


class DocumentLoaderFactory:
    @staticmethod
    def get_loader(file_path: str):
        extension = file_path.split('.')[-1].lower()
        if extension in ["pdf", "pptx", "docx", "xlsx", "html"]:
            return LlamaLoader(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {extension}")
