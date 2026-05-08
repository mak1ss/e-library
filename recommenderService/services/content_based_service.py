from typing import List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from utils.logger import logger
from models.request_response_models import (
    SimilarBookResponse, ExplanationDetails, ExplanationReasonType,
)
from services.ml_model_loader import MLModelLoader


class ContentBasedRecommender:
    """Content-based recommendation engine using TF-IDF similarity"""
    
    def __init__(self, ml_loader: MLModelLoader):
        self.ml_loader = ml_loader
    
    def get_similar_books(
        self,
        seed_book_id: int,
        top_k: int = 10,
        min_similarity_score: float = 0.0
    ) -> List[SimilarBookResponse]:
        """
        Get similar books using TF-IDF cosine similarity.
        
        Args:
            seed_book_id: The book to find similar books for
            top_k: Return top-k results
            min_similarity_score: Filter results below threshold
        
        Returns:
            List of (bookId, similarity_score) sorted by score (desc)
        """
        try:
            with self.ml_loader.lock:
                row_idx = self.ml_loader.bookid_to_row_mapping.get(str(seed_book_id))
                if row_idx is None:
                    logger.warning(f"Book {seed_book_id} not found in model")
                    return []
                seed_vector = self.ml_loader.book_embeddings[row_idx].copy()
                all_embeddings = self.ml_loader.book_embeddings
                row_to_bookid = {v: int(k) for k, v in self.ml_loader.bookid_to_row_mapping.items()}

            similarities = cosine_similarity(seed_vector.reshape(1, -1), all_embeddings)[0]
            similarities[row_idx] = -1
            top_indices = np.argsort(similarities)[-top_k:][::-1]

            results = []
            for idx in top_indices:
                sim_score = float(similarities[idx])
                if sim_score >= min_similarity_score:
                    results.append(SimilarBookResponse(
                        bookId=row_to_bookid[idx],
                        similarityScore=sim_score
                    ))

            logger.info(f"Found {len(results)} similar books for book {seed_book_id}")
            return results

        except Exception as e:
            logger.error(f"Error computing content-based similarity: {e}")
            return []

    def get_similar_books_with_explanations(
        self,
        seed_book_id: int,
        top_k: int = 10,
        min_similarity_score: float = 0.0
    ) -> List[SimilarBookResponse]:
        """
        Get similar books WITH explanation of why they're similar.
        Uses TF-IDF to extract top contributing terms.
        
        Args:
            seed_book_id: The book to find similar books for
            top_k: Return top-k results
            min_similarity_score: Filter results below threshold
        
        Returns:
            List of SimilarBookResponse with explanation of similarity
        """
        try:
            with self.ml_loader.lock:
                row_idx = self.ml_loader.bookid_to_row_mapping.get(str(seed_book_id))
                if row_idx is None:
                    logger.warning(f"Book {seed_book_id} not found in model")
                    return []
                seed_vector = self.ml_loader.book_embeddings[row_idx].copy()
                all_embeddings = self.ml_loader.book_embeddings
                row_to_bookid = {v: int(k) for k, v in self.ml_loader.bookid_to_row_mapping.items()}

            similarities = cosine_similarity(seed_vector.reshape(1, -1), all_embeddings)[0]
            similarities[row_idx] = -1
            top_indices = np.argsort(similarities)[-top_k:][::-1]

            results = []
            for idx in top_indices:
                sim_score = float(similarities[idx])
                if sim_score < min_similarity_score:
                    continue

                explanation = ExplanationDetails(
                    primaryReason=f"Semantic similarity: {sim_score:.2f}",
                    reasonType=ExplanationReasonType.EMBEDDING_SIMILARITY,
                    topContributors=[],
                    confidenceScore=sim_score,
                    details={"similarityScore": sim_score},
                )

                results.append(SimilarBookResponse(
                    bookId=row_to_bookid[idx],
                    similarityScore=sim_score,
                    explanation=explanation
                ))
            
            logger.info(f"Found {len(results)} similar books with explanations for book {seed_book_id}")
            return results
        
        except Exception as e:
            logger.error(f"Error computing content-based similarity with explanations: {e}")
            return []
