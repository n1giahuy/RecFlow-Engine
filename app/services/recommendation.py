from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import settings
from app.schemas.book import Book


class RecommendationService:
    """
    Service for handling book recommendations using LangChain.
    """

    def __init__(self):
        self.vector_store = None
        self.load_artifacts()

    def load_artifacts(self):
        """
        Loads all necessary artifacts into memory.
        - Embedding model
        - FAISS vector store
        """

        embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
        self.vector_store = FAISS.load_local(
            settings.faiss_index_path, embeddings, allow_dangerous_deserialization=True
        )

    def recommend(self, query, top_k, filter_category, filter_sentiment) -> list[Book]:
        """
        Get book recommendation base on the query and filters.
        Implements retrieve-then-filter approach.
        """
        candidate_docs = self.vector_store.similarity_search(
            query, k=settings.faiss_candidate_count
        )

        filtered_results = []
        titles = set()

        for doc in candidate_docs:
            if len(filtered_results) >= top_k:
                break

            metadata = doc.metadata

            if metadata.get("title") in titles:
                continue
            if (
                filter_category
                and metadata.get("predicted_category") != filter_category
            ):
                continue
            if filter_sentiment and metadata.get("sentiment") != filter_sentiment:
                continue

            filtered_results.append(Book(**metadata))
            titles.add(metadata["title"])

        return filtered_results
