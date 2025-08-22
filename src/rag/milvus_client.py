from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Optional
import logging
from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection, db
from src.rag.schemas.milvus import MilvusClientSchema
from src.config import settings


logger = logging.getLogger(__name__)


class MilvusHandler:
    def __init__(self, connect_params: MilvusClientSchema, dim: int = 384):
        self.create_database_if_not_exists(connect_params)
        self.dim = dim
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection_name = settings.COLLECTION_NAME

        # Connect to Milvus
        self._connect(connect_params)

        # Create collection if it doesn't exist
        self._create_collection()

        self.collection = Collection(self.collection_name)

    def create_database_if_not_exists(self, connect_params):
        """Create the database if it doesn't exist"""
        try:
            connections.connect(
                alias="default",
                host=connect_params.host,
                port=int(connect_params.port),
                user=connect_params.user if connect_params.user else None,
                password=connect_params.password if connect_params.password else None
            )
            databases = db.list_database()
            logging.info(f"Existing databases: {databases}")
            db_name = settings.MILVUS_DATABASE_NAME
            if db_name not in databases:
                db.create_database(db_name)
                logging.info(f"Created new database: {db_name}")
            else:
                logging.info(f"Database {db_name} already exists")

            db.using_database(db_name)
            logging.info(f"Now using database: {db_name}")

        except Exception as e:
            logging.error(f"Error creating/using database: {str(e)}")
            raise

    def _connect(self, connect_params):
        """Establish connection to Milvus"""
        try:
            connections.connect(
                host=connect_params.host,
                port=int(connect_params.port),
                user=connect_params.user,
                password=connect_params.password,
                db_name=settings.MILVUS_DATABASE_NAME
            )
            logger.info(f"Connected to Milvus at {connect_params.host}:{connect_params.port}")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise

    def _create_collection(self,):
        """Create collection if it doesn't exist"""
        if not utility.has_collection(self.collection_name):
            # Define fields
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dim)
            ]

            # Create schema
            schema = CollectionSchema(fields=fields, description="Technical documentation embeddings")

            # Create collection
            collection = Collection(name=self.collection_name, schema=schema)

            # Create index
            index_params = {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            }

            collection.create_index(field_name="embedding", index_params=index_params)
            logger.info(f"Created collection {self.collection_name} with index")
        else:
            logger.info(f"Collection {self.collection_name} already exists")

    def add_documents(self, documents: List[str], metadata: Optional[List[dict]] = None):
        """Add documents to Milvus"""
        if not documents:
            return

        # Generate embeddings
        embeddings = self.embedding_model.encode(documents).tolist()

        # Prepare data for insertion
        entities = [
            documents,  # text field
            embeddings  # embedding field
        ]

        # Insert data
        try:
            self.collection.insert(entities)
            logger.info(f"Inserted {len(documents)} documents into Milvus")
        except Exception as e:
            logger.error(f"Failed to insert documents: {e}")
            raise

        # Flush to make sure data is persisted
        self.collection.flush()

    def query(self, query_text: str, n_results: int = 5) -> List[str]:
        """Query Milvus for similar documents"""
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query_text]).tolist()

        # Search parameters
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

        # Execute search
        results = self.collection.search(
            data=query_embedding,
            anns_field="embedding",
            param=search_params,
            limit=n_results,
            output_fields=["text"]
        )

        # Extract results
        retrieved_docs = []
        for hits in results:
            for hit in hits:
                retrieved_docs.append(hit.entity.get("text"))

        return retrieved_docs

    def get_collection_stats(self) -> dict:
        """Get collection statistics"""
        stats = {}
        try:
            stats["num_entities"] = self.collection.num_entities
            stats["indexes"] = self.collection.indexes
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")

        return stats

    def close(self):
        """Close connection"""
        connections.disconnect('default')
        logger.info("Disconnected from Milvus")