from logging import getLogger

from langchain_community.vectorstores import Pinecone
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from config import config

logger = getLogger(__name__)

embeddings = OpenAIEmbeddings(model="text-embedding-3-large", openai_api_key=config.OPENAI_API_KEY)


def save_to_vectorstore(documents: list[Document]) -> None:
    try:
        Pinecone.from_documents(
            documents,
            embeddings,
            index_name=config.PINECONE_INDEX_NAME
        )
    except Exception as e:
        logger.error(f"Error saving to vectorstore: {e}")


def get_vectorstore():
    return Pinecone.from_existing_index(config.PINECONE_INDEX_NAME, embeddings)
