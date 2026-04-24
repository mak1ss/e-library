from typing import List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from utils.logger import logger
from models.request_response_models import (
    SimilarBookResponse, ExplanationDetails, ExplanationReasonType
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
            # Get row index for seed book
            row_idx = self.ml_loader.bookid_to_row_mapping.get(str(seed_book_id))
            if row_idx is None:
                logger.warning(f"Book {seed_book_id} not found in model")
                return []
            
            # Get seed book's TF-IDF vector
            seed_vector = self.ml_loader.tfidf_matrix[row_idx]
            
            # Compute cosine similarity with all books
            # If sparse matrix, use scipy.sparse.csr_matrix.dot
            similarities = cosine_similarity(
                seed_vector.reshape(1, -1),
                self.ml_loader.tfidf_matrix
            )[0]
            
            # Exclude seed book itself (similarity = 1.0)
            similarities[row_idx] = -1
            
            # Get top-k indices
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            # Map indices back to book IDs
            row_to_bookid = {v: int(k) for k, v in self.ml_loader.bookid_to_row_mapping.items()}
            
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
            # Get row index for seed book
            row_idx = self.ml_loader.bookid_to_row_mapping.get(str(seed_book_id))
            if row_idx is None:
                logger.warning(f"Book {seed_book_id} not found in model")
                return []
            
            # Get seed book's TF-IDF vector
            seed_vector = self.ml_loader.tfidf_matrix[row_idx]
            
            # Compute cosine similarity with all books
            similarities = cosine_similarity(
                seed_vector.reshape(1, -1),
                self.ml_loader.tfidf_matrix
            )[0]
            
            # Exclude seed book itself
            similarities[row_idx] = -1
            
            # Get top-k indices
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            # Get feature names (TF-IDF terms)
            feature_names = self.ml_loader.tfidf_vectorizer.get_feature_names_out()
            
            # Map indices back to book IDs
            row_to_bookid = {v: int(k) for k, v in self.ml_loader.bookid_to_row_mapping.items()}
            
            results = []
            for idx in top_indices:
                sim_score = float(similarities[idx])
                if sim_score < min_similarity_score:
                    continue
                
                # Extract top contributing terms
                similar_vector = self.ml_loader.tfidf_matrix[idx]
                
                # Element-wise product of vectors = terms that appear in BOTH books
                # This shows which topics/terms create the similarity
                if hasattr(seed_vector, 'multiply'):
                    # Sparse matrix case
                    shared_terms = seed_vector.multiply(similar_vector)
                    shared_array = shared_terms.toarray().flatten()
                else:
                    # Dense matrix case
                    shared_array = seed_vector * similar_vector
                
                # Get indices of top 5 contributing terms
                top_term_indices = np.argsort(shared_array)[-5:][::-1]
                top_terms = [
                    feature_names[i] 
                    for i in top_term_indices 
                    if shared_array[i] > 0
                ]
                
                # Build explanation
                num_matching_terms = len([t for t in top_terms if t])
                explanation = ExplanationDetails(
                    primaryReason=f"Content similarity: {num_matching_terms} matching topics",
                    reasonType=ExplanationReasonType.TF_IDF_MATCH,
                    topContributors=top_terms[:5],
                    confidenceScore=sim_score,
                    details={
                        "matchingTerms": num_matching_terms,
                        "similarityScore": sim_score
                    }
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
