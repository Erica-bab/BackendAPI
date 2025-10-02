from fastapi import APIRouter

from app.api.v1.endpoints import meal, rating, keyword

api_router = APIRouter()

api_router.include_router(meal.router, prefix="/meals", tags=["meals"])
api_router.include_router(rating.router, prefix="/ratings", tags=["ratings"])
api_router.include_router(keyword.router, prefix="/keywords", tags=["keywords"])

