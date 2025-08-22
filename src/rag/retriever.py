from .milvus_client import MilvusHandler
from .document_processor import DocumentProcessor
from typing import List, Optional
import logging
from src.rag.schemas.milvus import MilvusClientSchema
from src.config import settings


logger = logging.getLogger(__name__)


class RAGSystem:
    def __init__(self):
        connect_params = MilvusClientSchema(host=settings.MILVUS_HOST,
                                            port=settings.MILVUS_PORT,
                                            user=settings.MILVUS_USER,
                                            password=settings.MILVUS_PASSWORD,
                                            db_name=settings.MILVUS_DATABASE_NAME)
        self.vector_store = MilvusHandler(connect_params)
        self.document_processor = DocumentProcessor()

    def add_document(self, pdf_path: str):
        """Process and add a single PDF document to Milvus"""
        try:
            text = self.document_processor.extract_text_from_pdf(pdf_path)
            chunks = self.document_processor.split_text_into_chunks(text)
            self.vector_store.add_documents(chunks)
            logger.info(f"Added document {pdf_path} to Milvus")
        except Exception as e:
            logger.error(f"Failed to add document {pdf_path}: {e}")
            raise

    def add_documents_from_directory(self, directory_path: str):
        """Process and add all PDFs from a directory to Milvus"""
        import os

        pdf_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.pdf')]

        for pdf_file in pdf_files:
            pdf_path = os.path.join(directory_path, pdf_file)
            self.add_document(pdf_path)

    def query(self, question: str, n_results: int = 5) -> List[str]:
        """Query the RAG system"""
        return self.vector_store.query(question, n_results)

    def get_stats(self) -> dict:
        """Get system statistics"""
        return self.vector_store.get_collection_stats()

    def close(self):
        """Close connections"""
        self.vector_store.close()