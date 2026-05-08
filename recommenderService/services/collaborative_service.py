from typing import List
import numpy as np
from utils.logger import logger
from models.request_response_models import (
    PersonalizedRecommendationResponse, ExplanationDetails, ExplanationReasonType,
    SeedBook,
)
from services.ml_model_loader import MLModelLoader


class CollaborativeRecommender:
    """
    Item-item collaborative filtering using co-occurrence matrix.

    Pre-computed co-occurrence matrix: co_matrix[i][j] = Σ min(r_i, r_j)/5 over
    users who reviewed both book_i and book_j, so mutually-liked pairs score higher
    than mixed-sentiment pairs.  At query time each seed row is further scaled by
    the requesting user's own rating of that seed book (seed_rating / 5).
    """

    def __init__(self, ml_loader: MLModelLoader):
        self.ml_loader = ml_loader

    def get_personalized_recommendations(
        self,
        user_seed_books: List[SeedBook],
        top_k: int = 10
    ) -> List[PersonalizedRecommendationResponse]:
        """
        Get recommendations based on user's review history (seed books).
        Algorithm:
          1. For each seed book, fetch its co-occurrence row and scale it by
             seed_rating / 5 (user's own opinion of that seed).
          2. Aggregate scaled scores across all seed books.
          3. Exclude seed books from results.
          4. Return top-k by aggregated score.
        """
        try:
            if not user_seed_books:
                return []

            seed_indices = []
            for seed in user_seed_books:
                row_idx = self.ml_loader.bookid_to_row_mapping.get(str(seed.bookId))
                if row_idx is not None:
                    seed_indices.append((seed.bookId, seed.rating, row_idx))

            if not seed_indices:
                logger.warning(f"No seed books found in model: {[s.bookId for s in user_seed_books]}")
                return []

            with self.ml_loader.lock:
                n = self.ml_loader.item_cooccurrence_matrix.shape[0]
                cooccurrence_scores = np.zeros(n)
                for _, seed_rating, seed_idx in seed_indices:
                    cooccurrence_scores += (
                        self.ml_loader.item_cooccurrence_matrix[seed_idx] * (seed_rating / 5.0)
                    )
                row_to_bookid = {v: int(k) for k, v in self.ml_loader.bookid_to_row_mapping.items()}

            for _, _, seed_idx in seed_indices:
                cooccurrence_scores[seed_idx] = -1

            top_indices = np.argsort(cooccurrence_scores)[-top_k:][::-1]

            results = []
            for idx in top_indices:
                if cooccurrence_scores[idx] >= 0:
                    results.append(PersonalizedRecommendationResponse(
                        bookId=row_to_bookid[idx],
                        score=float(cooccurrence_scores[idx])
                    ))

            logger.info(
                f"Generated {len(results)} personalized recommendations "
                f"for user with {len(user_seed_books)} reviewed books"
            )
            return results

        except Exception as e:
            logger.error(f"Error computing collaborative recommendations: {e}")
            return []

    def get_personalized_recommendations_with_explanations(
        self,
        user_seed_books: List[SeedBook],
        top_k: int = 10
    ) -> List[PersonalizedRecommendationResponse]:
        """
        Get recommendations WITH explanation about which seed book influenced each
        recommendation.
        """
        try:
            if not user_seed_books:
                return []

            seed_indices = []
            for seed in user_seed_books:
                row_idx = self.ml_loader.bookid_to_row_mapping.get(str(seed.bookId))
                if row_idx is not None:
                    seed_indices.append((seed.bookId, seed.rating, row_idx))

            if not seed_indices:
                logger.warning(f"No seed books found in model: {[s.bookId for s in user_seed_books]}")
                return []

            with self.ml_loader.lock:
                n = self.ml_loader.item_cooccurrence_matrix.shape[0]
                cooccurrence_scores = np.zeros(n)
                seed_contributions = {}  # recommended_idx -> {seed_book_id: weighted_score}

                for seed_book_id, seed_rating, seed_idx in seed_indices:
                    seed_weight = seed_rating / 5.0
                    cooc_row = self.ml_loader.item_cooccurrence_matrix[seed_idx]
                    if hasattr(cooc_row, 'toarray'):
                        cooc_values = cooc_row.toarray().flatten()
                    else:
                        cooc_values = np.array(cooc_row)
                    weighted_values = cooc_values * seed_weight

                    for rec_idx, score in enumerate(weighted_values):
                        cooccurrence_scores[rec_idx] += score
                        if rec_idx not in seed_contributions:
                            seed_contributions[rec_idx] = {}
                        seed_contributions[rec_idx][seed_book_id] = float(score)

                row_to_bookid = {v: int(k) for k, v in self.ml_loader.bookid_to_row_mapping.items()}

            for _, _, seed_idx in seed_indices:
                cooccurrence_scores[seed_idx] = -1

            top_indices = np.argsort(cooccurrence_scores)[-top_k:][::-1]

            results = []
            for idx in top_indices:
                if cooccurrence_scores[idx] < 0:
                    continue

                contrib = seed_contributions.get(idx, {})
                if not contrib:
                    continue

                most_influential_id, _ = max(contrib.items(), key=lambda x: x[1])

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

            logger.info(
                f"Generated {len(results)} personalized recommendations with explanations "
                f"for user with {len(user_seed_books)} reviewed books"
            )
            return results

        except Exception as e:
            logger.error(f"Error computing collaborative recommendations with explanations: {e}")
            return []
