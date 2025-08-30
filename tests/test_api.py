from fastapi.testclient import TestClient
from app.main import app


def test_read_root():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to RecFlow Engine API."}


def test_recommend_success(mocker):
    """
    Test the /recommend endpoint for a successful response.
    """
    with TestClient(app) as client:
        mock_results = [
            {
                "title": "Mock book 1",
                "authors": "Author A",
                "thumbnail": "",
                "predicted_category": "Science fiction",
                "sentiment": "POSITIVE",
                "average_rating": 5.5,
            }
        ]
        mocker.patch(
            "app.services.recommendation.RecommendationService.recommend",
            return_value=mock_results,
        )

        response = client.post(
            "/api/v1/recommend", json={"query": "sci-fi adventure", "top_k": 1}
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "results" in response_data
        assert len(response_data["results"]) == 1
        assert response_data["results"][0]["title"] == "Mock book 1"


def test_recommend_validation():
    """
    Test for validation error
    """
    with TestClient(app) as client:
        response = client.post("/api/v1/recommend", json={"query": "a", "top_k": 5})
        assert response.status_code == 422


def test_recommend_filter_passing(mocker):
    """
    Test if filter parameters are correctly passed
    """
    with TestClient(app) as client:
        mock_recommend = mocker.patch(
            "app.services.recommendation.RecommendationService.recommend",
            return_value=[],
        )
        client.post(
            "/api/v1/recommend",
            json={
                "query": "A positive fantasy book",
                "top_k": 5,
                "filter_category": "Fantasy",
                "filter_sentiment": "POSITIVE",
            },
        )
        mock_recommend.assert_called_once_with(
            query="A positive fantasy book",
            top_k=5,
            filter_category="Fantasy",
            filter_sentiment="POSITIVE",
        )
