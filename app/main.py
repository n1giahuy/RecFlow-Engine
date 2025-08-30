from fastapi import FastAPI
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator

from app.api import router as api_router
from app.services.recommendation import RecommendationService
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan manager for the FastAPI application
    """
    app.state.engine = RecommendationService()
    yield
    app.state.engine = None


app = FastAPI(
    title=settings.app_name,
    description="A book recommender system using ML and MLOps principles.",
    version=settings.app_version,
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to RecFlow Engine API."}


@app.get("/error", tags=["Test"])
def make_error():
    result = 1 / 0
    return {"result": result}
