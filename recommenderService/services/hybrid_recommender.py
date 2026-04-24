from typing import List
from models.request_response_models import SimilarBookResponse, PersonalizedRecommendationResponse
from services.content_based_service import ContentBasedRecommender
from services.collaborative_service import CollaborativeRecommender


class HybridRecommender:
    """Hybrid recommendation orchestrator combining content-based and collaborative filtering"""
    
    def __init__(self, content_based: ContentBasedRecommender, collaborative: CollaborativeRecommender):
        self.content_based = content_based
        self.collaborative = collaborative
    
    def get_similar_books(self, book_id: int, top_k: int = 10) -> List[SimilarBookResponse]:
        """Delegates to content-based engine"""
        return self.content_based.get_similar_books(book_id, top_k)
    
    def get_personalized_recommendations(
        self,
        user_seed_books: List[int],
        top_k: int = 10,
        use_cache: bool = True,
        cache_ttl_hours: int = 24
    ) -> List[PersonalizedRecommendationResponse]:
        """
        Get personalized recommendations (delegated to collaborative).
        Can be wrapped with caching logic (implemented in bookService via MongoDB).
        """
        return self.collaborative.get_personalized_recommendations(user_seed_books, top_k)
