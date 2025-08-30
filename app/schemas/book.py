from typing import List, Optional
from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """
    Schema for the recommendation request body
    """

    query: str = Field(
        ...,
        description="The search query for book recommendations.",
        min_length=3,
        example="A magical school for young wizards.",
    )
    top_k: int = Field(
        default=10, ge=1, le=50, description="Number of recommendations to return."
    )
    filter_category: Optional[str] = Field(
        default=None, description="Filter by category.", example="Fantasy"
    )
    filter_sentiment: Optional[str] = Field(
        default=None, description="Filter by sentiment.", example="POSITIVE"
    )


class Book(BaseModel):
    """
    Schema representing a single book in the response
    """

    title: str
    authors: str
    thumbnail: Optional[str]
    predicted_category: str
    sentiment: str
    average_rating: float


class RecommendationResponse(BaseModel):
    """
    Schema for the final API response
    """

    results: List[Book]
