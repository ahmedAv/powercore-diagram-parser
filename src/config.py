from dotenv import load_dotenv
import os

load_dotenv(override=True)


class Settings:

    MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
    MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
    MILVUS_USER = os.getenv("MILVUS_USER", "")
    MILVUS_PASSWORD = os.getenv("MILVUS_PASSWORD", "")
    MILVUS_DATABASE_NAME = os.getenv("MILVUS_DATABASE_NAME", "default")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "face_encodings")


settings = Settings()
