from typing import List
import numpy as np
from utils.logger import logger
from models.request_response_models import (
    PersonalizedRecommendationResponse, ExplanationDetails, ExplanationReasonType
)
from services.ml_model_loader import MLModelLoader


class CollaborativeRecommender:
    """
    Item-item collaborative filtering using co-occurrence matrix.
    Pre-computed co-occurrence matrix: co_matrix[i][j] = count of users who reviewed both book_i and book_j
    """
    
    def __init__(self, ml_loader: MLModelLoader):
        self.ml_loader = ml_loader
    
    def get_personalized_recommendations(
        self,
        user_seed_books: List[int],
        top_k: int = 10
    ) -> List[PersonalizedRecommendationResponse]:
        """
        Get recommendations based on user's review history (seed books).
        Algorithm:
          1. For each seed book, find books that frequently co-occur with it
          2. Aggregate co-occurrence scores across all seed books
          3. Exclude seed books from results
          4. Return top-k by aggregated score
        
        Args:
            user_seed_books: List of book IDs user has reviewed
            top_k: Return top-k recommendations
        
        Returns:
            List of (bookId, co_occurrence_score) sorted by score (desc)
        """
        try:
            if not user_seed_books:
                return []
            
            # Map book IDs to row indices
            seed_indices = []
            for book_id in user_seed_books:
                row_idx = self.ml_loader.bookid_to_row_mapping.get(str(book_id))
                if row_idx is not None:
                    seed_indices.append(row_idx)
            
            if not seed_indices:
                logger.warning(f"No seed books found in model: {user_seed_books}")
                return []
            
            # Aggregate co-occurrence scores
            cooccurrence_scores = np.zeros(self.ml_loader.item_cooccurrence_matrix.shape[0])
            
            for seed_idx in seed_indices:
                # Add co-occurrence values for this seed book to all other books
                if isinstance(self.ml_loader.item_cooccurrence_matrix, np.ndarray):
                    cooccurrence_scores += self.ml_loader.item_cooccurrence_matrix[seed_idx]
            
            # Zero out seed books themselves
            for seed_idx in seed_indices:
                cooccurrence_scores[seed_idx] = -1
            
            # Get top-k recommendations
            top_indices = np.argsort(cooccurrence_scores)[-top_k:][::-1]
            
            # Map back to book IDs
            row_to_bookid = {v: int(k) for k, v in self.ml_loader.bookid_to_row_mapping.items()}
            
            results = []
            for idx in top_indices:
                if cooccurrence_scores[idx] >= 0:  # Filter out -1 (seed books)
                    results.append(PersonalizedRecommendationResponse(
                        bookId=row_to_bookid[idx],
                        score=float(cooccurrence_scores[idx])
                    ))
            
            logger.info(f"Generated {len(results)} personalized recommendations for user with {len(user_seed_books)} reviewed books")
            return results
        
        except Exception as e:
            logger.error(f"Error computing collaborative recommendations: {e}")
            return []
    
    def get_personalized_recommendations_with_explanations(
        self,
        user_seed_books: List[int],
        top_k: int = 10
    ) -> List[PersonalizedRecommendationResponse]:
        """
        Get recommendations WITH explanation about which seed book influenced each recommendation.
        
        Args:
            user_seed_books: List of book IDs user has reviewed
            top_k: Return top-k recommendations
        
        Returns:
            List of PersonalizedRecommendationResponse with explanation and seed book tracking
        """
        try:
            if not user_seed_books:
                return []
            
            # Map book IDs to row indices
            seed_indices = []
            for book_id in user_seed_books:
                row_idx = self.ml_loader.bookid_to_row_mapping.get(str(book_id))
                if row_idx is not None:
                    seed_indices.append((book_id, row_idx))
            
            if not seed_indices:
                logger.warning(f"No seed books found in model: {user_seed_books}")
                return []
            
            row_to_bookid = {v: int(k) for k, v in self.ml_loader.bookid_to_row_mapping.items()}
            cooccurrence_scores = np.zeros(self.ml_loader.item_cooccurrence_matrix.shape[0])
            
            # Track which seed book contributed most to each recommendation
            seed_contributions = {}  # recommended_idx -> {seed_book_id: score}
            
            for seed_book_id, seed_idx in seed_indices:
                cooc_row = self.ml_loader.item_cooccurrence_matrix[seed_idx]
                
                # Handle both sparse and dense arrays
                if hasattr(cooc_row, 'toarray'):
                    cooc_values = cooc_row.toarray().flatten()
                else:
                    cooc_values = cooc_row
                
                for rec_idx, score in enumerate(cooc_values):
                    cooccurrence_scores[rec_idx] += score
                    
                    # Track contribution from this seed book
                    if rec_idx not in seed_contributions:
                        seed_contributions[rec_idx] = {}
                    seed_contributions[rec_idx][seed_book_id] = float(score)
            
            # Zero out seed books themselves
            for seed_book_id, seed_idx in seed_indices:
                cooccurrence_scores[seed_idx] = -1
            
            # Get top-k
            top_indices = np.argsort(cooccurrence_scores)[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                if cooccurrence_scores[idx] < 0:
                    continue
                
                # Find which seed book(s) influenced this recommendation
                contrib = seed_contributions.get(idx, {})
                if not contrib:
                    continue
                
                # Get the seed book that most influenced this
                most_influential_book = max(contrib.items(), key=lambda x: x[1])
                most_influential_id, influence_score = most_influential_book
                
                # Build explanation (will be enriched on Java side with actual title)
                explanation = ExplanationDetails(
                    primaryReason=f"Based on your review of book {most_influential_id}",
                    reasonType=ExplanationReasonType.COLLABORATIVE_FILTER,
                    topContributors=[str(most_influential_id)],
                    confidenceScore=float(cooccurrence_scores[idx]),
                    details={
                        "influencedBySeedBooks": list(contrib.keys()),
                        "cooccurrenceScore": float(cooccurrence_scores[idx])
                    }
                )
                
                results.append(PersonalizedRecommendationResponse(
                    bookId=row_to_bookid[idx],
                    score=float(cooccurrence_scores[idx]),
                    explanation=explanation,
                    seedBookIds=[most_influential_id]
                ))
            
            logger.info(f"Generated {len(results)} personalized recommendations with explanations for user with {len(user_seed_books)} reviewed books")
            return results
        
        except Exception as e:
            logger.error(f"Error computing collaborative recommendations with explanations: {e}")
            return []
