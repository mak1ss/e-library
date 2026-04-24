from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from utils.logger import logger
from models.request_response_models import (
    SimilarBookResponse,
    PersonalizedRecommendationResponse,
    GetSimilarBooksRequest,
    GetPersonalizedRecommendationsRequest,
    HealthCheckResponse
)

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])

# Will be populated by main.py via dependency injection
ml_loader = None
recommender = None


def set_recommender_context(loader, recommender_instance):
    """Set recommender context (called from main.py)"""
    global ml_loader, recommender
    ml_loader = loader
    recommender = recommender_instance


@router.get("/health", response_model=HealthCheckResponse, tags=["health"])
async def health_check():
    """Check if recommenderService is healthy and models are loaded"""
    return HealthCheckResponse(
        status="healthy",
        modelsLoaded=ml_loader.is_ready() if ml_loader else False,
        modelMetadata=ml_loader.model_metadata if ml_loader else None
    )


@router.post("/similar-books", response_model=List[SimilarBookResponse])
async def get_similar_books(request: GetSimilarBooksRequest):
    """
    Get similar books to a given book using content-based filtering (TF-IDF).
    Real-time computation (no caching). Returns explanation of why books are similar.
    
    Example:
        POST /api/v1/recommendations/similar-books
        {
            "bookId": 42,
            "topK": 10
        }
    
    Response:
        [
            {
                "bookId": 15,
                "similarityScore": 0.87,
                "explanation": {
                    "primaryReason": "Content similarity: 5 matching topics",
                    "reasonType": "TF_IDF_MATCH",
                    "topContributors": ["mystery", "thriller", "detective", "london", "crime"],
                    "confidenceScore": 0.87
                }
            },
            ...
        ]
    """
    try:
        if not recommender:
            raise HTTPException(status_code=503, detail="Recommender service not initialized")
        
        # Use new method with explanations
        recommendations = recommender.content_based.get_similar_books_with_explanations(
            request.bookId, request.topK
        )
        return recommendations
    except Exception as e:
        logger.error(f"Error getting similar books: {e}")
        raise HTTPException(status_code=500, detail="Failed to compute similar books")


@router.post("/personalized", response_model=List[PersonalizedRecommendationResponse])
async def get_personalized_recommendations(request: GetPersonalizedRecommendationsRequest):
    """
    Get personalized recommendations for a user based on their review history.
    Uses item-item collaborative filtering (co-occurrence matrix).
    Returns explanation about which seed book influenced each recommendation.
    
    Example:
        POST /api/v1/recommendations/personalized
        {
            "userSeedBooks": [3, 7, 15, 22],
            "topK": 10
        }
    
    Response:
        [
            {
                "bookId": 45,
                "score": 12.5,
                "seedBookIds": [3],
                "explanation": {
                    "primaryReason": "Based on your review of book 3",
                    "reasonType": "COLLABORATIVE_FILTER",
                    "topContributors": ["3"],
                    "confidenceScore": 12.5
                }
            },
            ...
        ]
    """
    try:
        if not recommender:
            raise HTTPException(status_code=503, detail="Recommender service not initialized")
        
        # Use new method with explanations
        recommendations = recommender.collaborative.get_personalized_recommendations_with_explanations(
            request.userSeedBooks,
            request.topK
        )
        return recommendations
    except Exception as e:
        logger.error(f"Error getting personalized recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to compute recommendations")


@router.post("/similar-books-batch")
async def get_similar_books_batch(request: Dict[str, Any]):
    """
    Batch query for similar books.
    Input: {"bookIds": [1, 2, 3], "topK": 10}
    Output: {"1": [similar book responses], "2": [...], ...}
    """
    try:
        if not recommender:
            raise HTTPException(status_code=503, detail="Recommender service not initialized")
        
        book_ids = request.get("bookIds", [])
        top_k = request.get("topK", 10)
        
        results = {}
        for bid in book_ids:
            results[str(bid)] = recommender.get_similar_books(bid, top_k)
        
        return results
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        raise HTTPException(status_code=500, detail="Failed to process batch request")
