from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class KeywordBase(BaseModel):
    """키워드 기본 스키마"""
    name: str = Field(..., max_length=50, description="키워드 이름")
    category: Optional[str] = Field(None, max_length=20, description="키워드 카테고리")


class KeywordCreate(KeywordBase):
    """키워드 생성"""
    display_order: int = Field(default=0, description="표시 순서")


class KeywordResponse(KeywordBase):
    """키워드 응답"""
    id: int
    display_order: int
    
    class Config:
        from_attributes = True


class KeywordReviewCreate(BaseModel):
    """키워드 리뷰 생성"""
    meal_id: int = Field(..., description="메뉴 ID")
    keyword_id: int = Field(..., description="키워드 ID")
    user_id: str = Field(..., min_length=1, max_length=100, description="사용자 ID")


class KeywordReviewResponse(BaseModel):
    """키워드 리뷰 응답"""
    id: int
    meal_id: int
    keyword_id: int
    keyword_name: str = Field(..., description="키워드 이름")
    user_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class MealKeywordStats(BaseModel):
    """메뉴 키워드 통계"""
    keyword_id: int
    keyword_name: str
    count: int = Field(..., description="선택된 횟수")


class MealKeywordStatsResponse(BaseModel):
    """메뉴 키워드 통계 응답"""
    meal_id: int
    keywords: List[MealKeywordStats] = Field(..., description="상위 키워드 목록")

