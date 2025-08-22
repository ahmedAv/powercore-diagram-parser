#!/usr/bin/env python3
"""
Script to setup and initialize Milvus for the RAG system
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.rag.milvus_client import MilvusHandler
from src.rag.document_processor import DocumentProcessor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_milvus():
    """Initialize Milvus connection and verify setup"""
    try:
        # Test connection
        vector_store = MilvusHandler()
        stats = vector_store.get_collection_stats()
        logger.info(f"Milvus setup successful. Collection stats: {stats}")
        vector_store.close()
        return True
    except Exception as e:
        logger.error(f"Milvus setup failed: {e}")
        return False


def load_initial_documents(documents_dir: str):
    """Load initial documents into Milvus"""
    if not os.path.exists(documents_dir):
        logger.warning(f"Documents directory {documents_dir} does not exist")
        return

    from src.rag.retriever import RAGSystem

    rag_system = RAGSystem()

    try:
        rag_system.add_documents_from_directory(documents_dir)
        stats = rag_system.get_stats()
        logger.info(f"Loaded documents successfully. Stats: {stats}")
    except Exception as e:
        logger.error(f"Failed to load documents: {e}")
    finally:
        rag_system.close()


if __name__ == "__main__":
    # Setup Milvus
    success = setup_milvus()

    if success:
        # Load documents from default directory
        documents_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'documents')
        load_initial_documents(documents_dir)

    sys.exit(0 if success else 1)