from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class ExplanationReasonType(str, Enum):
    """Types of recommendation explanations"""
    TF_IDF_MATCH = "TF_IDF_MATCH"
    COLLABORATIVE_FILTER = "COLLABORATIVE_FILTER"


class ExplanationDetails(BaseModel):
    """Why a book was recommended"""
    primaryReason: str
    reasonType: ExplanationReasonType
    topContributors: List[str] = Field(default_factory=list)  # Keywords or seed book IDs
    confidenceScore: float
    details: Optional[Dict[str, Any]] = None


class SimilarBookResponse(BaseModel):
    """Response model for similar books"""
    bookId: int
    similarityScore: float
    explanation: Optional[ExplanationDetails] = None


class PersonalizedRecommendationResponse(BaseModel):
    """Response model for personalized recommendations"""
    bookId: int
    score: float
    explanation: Optional[ExplanationDetails] = None
    seedBookIds: Optional[List[int]] = None


class GetSimilarBooksRequest(BaseModel):
    """Request model for getting similar books"""
    bookId: int = Field(..., description="The book ID to find similar books for")
    topK: int = Field(default=10, ge=1, le=50, description="Number of recommendations")


class GetPersonalizedRecommendationsRequest(BaseModel):
    """Request model for getting personalized recommendations"""
    userSeedBooks: List[int] = Field(
        ..., 
        description="List of book IDs user has reviewed"
    )
    topK: int = Field(default=10, ge=1, le=50, description="Number of recommendations")


class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str
    modelsLoaded: bool
    modelMetadata: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    status_code: int
