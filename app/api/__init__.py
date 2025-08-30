from fastapi import APIRouter, Depends, Request
from typing import Dict

from app.services.recommendation import RecommendationService
from app.schemas.book import RecommendationRequest, RecommendationResponse

service_container: Dict[str, RecommendationService] = {}


def get_recommendation_service(request: Request):
    """
    Dependency injector for the RecommendationService.
    """
    return request.app.state.engine


router = APIRouter()


@router.post(
    "/recommend",
    response_model=RecommendationResponse,
    summary="Get book recommendations",
)
def recommend_book(
    request: RecommendationRequest,
    service: RecommendationService = Depends(get_recommendation_service),
):
    """
    Endpoint to get book recommendations.
    It uses the RecommendationService to perform the logics
    """
    results = service.recommend(
        query=request.query,
        top_k=request.top_k,
        filter_category=request.filter_category,
        filter_sentiment=request.filter_sentiment,
    )
    return RecommendationResponse(results=results)
