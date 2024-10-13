import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Config(BaseSettings):
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    UPLOAD_FOLDER: str = "uploads"


config = Config()
