from src.rag.retriever import RAGSystem

rag_system = RAGSystem()

relevant_info = rag_system.query(
                "pydantic ",
                n_results=1
            )