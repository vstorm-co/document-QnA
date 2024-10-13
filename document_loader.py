from abc import ABC, abstractmethod
from logging import getLogger
from typing import Optional

from langchain_community.document_loaders import PyPDFLoader, UnstructuredMarkdownLoader, UnstructuredExcelLoader, \
    CSVLoader as CSVDocumentLoader, Docx2txtLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = getLogger(__name__)


class DocumentLoader(ABC):
    def __init__(self, file_path: str):
        self.file_path = file_path

    @abstractmethod
    def load(self) -> list[Document] | None:
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


class PDFLoader(DocumentLoader):
    def load(self) -> list[Document] | None:
        try:
            loader = PyPDFLoader(self.file_path)
            return loader.load_and_split()
        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            return None


class DOCXLoader(DocumentLoader):
    def load(self) -> list[Document] | None:
        try:
            loader = Docx2txtLoader(self.file_path)
            return loader.load_and_split()
        except Exception as e:
            logger.error(f"Error loading DOCX: {e}")
            return None


class CSVLoader(DocumentLoader):
    def load(self) -> list[Document] | None:
        try:
            loader = CSVDocumentLoader(self.file_path)
            return loader.load_and_split()
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            return None


class XLSXLoader(DocumentLoader):
    def load(self) -> list[Document] | None:
        try:
            loader = UnstructuredExcelLoader(self.file_path)
            return loader.load_and_split()
        except Exception as e:
            logger.error(f"Error loading XLSX: {e}")
            return None


class MarkdownLoader(DocumentLoader):
    def load(self) -> list[Document] | None:
        try:
            loader = UnstructuredMarkdownLoader(self.file_path)
            return loader.load()
        except Exception as e:
            logger.error(f"Error loading MD: {e}")
            return None


class TXTLoader(DocumentLoader):
    def load(self) -> list[Document] | None:
        try:
            with open(self.file_path, "r") as file:
                data = file.read()
                return [Document(page_content=data)]
        except Exception as e:
            logger.error(f"Error loading TXT: {e}")
            return None


class DocumentLoaderFactory:
    @staticmethod
    def get_loader(file_path):
        extension = file_path.split('.')[-1].lower()
        if extension == 'pdf':
            return PDFLoader(file_path)
        elif extension == 'md':
            return MarkdownLoader(file_path)
        elif extension == 'txt':
            return TXTLoader(file_path)
        elif extension == 'csv':
            return CSVLoader(file_path)
        elif extension == 'xlsx':
            return XLSXLoader(file_path)
        elif extension == 'docx':
            return DOCXLoader(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {extension}")
