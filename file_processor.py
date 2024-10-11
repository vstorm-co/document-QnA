from logging import getLogger

from document_loader import DocumentLoaderFactory
from vector_store import save_to_vectorstore

logger = getLogger(__name__)


def process_file(file_path: str) -> bool:
    try:
        document_loader = DocumentLoaderFactory.get_loader(file_path)
        loaded_documents = document_loader.load()
        logger.info(f"Loaded {len(loaded_documents)} documents")

        split_documents = document_loader.split_documents(loaded_documents)
        logger.info(f"Split into {len(split_documents)} chunks")
        save_to_vectorstore(split_documents)

        return True
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return False
