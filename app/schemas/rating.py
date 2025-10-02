from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class RatingBase(BaseModel):
    """평점 기본 스키마"""
    rating: float = Field(..., ge=1.0, le=5.0, description="평점 (1.0 ~ 5.0)")


class RatingCreate(RatingBase):
    """평점 생성"""
    meal_id: int = Field(..., description="메뉴 ID")
    user_id: str = Field(..., min_length=1, max_length=100, description="사용자 ID")


class RatingUpdate(RatingBase):
    """평점 수정"""
    pass


class RatingResponse(RatingBase):
    """평점 응답"""
    id: int
    meal_id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MealRatingStats(BaseModel):
    """메뉴 평점 통계"""
    meal_id: int
    average_rating: float = Field(..., description="평균 평점")
    rating_count: int = Field(..., description="평점 개수")
    rating_distribution: dict = Field(..., description="평점 분포 {1: 10, 2: 5, ...}")

