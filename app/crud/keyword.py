from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from app.models.keyword import Keyword, MealKeywordReview
from app.schemas.keyword import (
    KeywordCreate, KeywordReviewCreate, 
    MealKeywordStats, MealKeywordStatsResponse
)


def create_keyword(db: Session, keyword_data: KeywordCreate) -> Keyword:
    """키워드 생성"""
    keyword = Keyword(**keyword_data.model_dump())
    db.add(keyword)
    db.commit()
    db.refresh(keyword)
    return keyword


def get_all_keywords(db: Session) -> List[Keyword]:
    """모든 키워드 조회"""
    return db.query(Keyword).order_by(Keyword.display_order, Keyword.name).all()


def get_keywords_by_category(db: Session, category: str) -> List[Keyword]:
    """카테고리별 키워드 조회"""
    return db.query(Keyword).filter(Keyword.category == category).order_by(Keyword.display_order, Keyword.name).all()


def get_keyword_by_id(db: Session, keyword_id: int) -> Keyword:
    """키워드 ID로 조회"""
    return db.query(Keyword).filter(Keyword.id == keyword_id).first()


def create_keyword_review(
    db: Session,
    review_data: KeywordReviewCreate
) -> MealKeywordReview:
    """키워드 리뷰 생성"""
    # 중복 체크
    existing = db.query(MealKeywordReview).filter(
        MealKeywordReview.meal_id == review_data.meal_id,
        MealKeywordReview.keyword_id == review_data.keyword_id,
        MealKeywordReview.user_id == review_data.user_id
    ).first()
    
    if existing:
        # 이미 존재하면 그대로 반환 (중복 방지)
        return existing
    
    review = MealKeywordReview(**review_data.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def delete_keyword_review(
    db: Session,
    meal_id: int,
    keyword_id: int,
    user_id: str
) -> bool:
    """키워드 리뷰 삭제"""
    review = db.query(MealKeywordReview).filter(
        MealKeywordReview.meal_id == meal_id,
        MealKeywordReview.keyword_id == keyword_id,
        MealKeywordReview.user_id == user_id
    ).first()
    
    if review:
        db.delete(review)
        db.commit()
        return True
    return False


def get_meal_keyword_stats(
    db: Session,
    meal_id: int,
    top_n: int = 10
) -> MealKeywordStatsResponse:
    """메뉴의 키워드 통계 (상위 N개)"""
    stats = db.query(
        Keyword.id,
        Keyword.name,
        func.count(MealKeywordReview.id).label('count')
    ).join(
        MealKeywordReview, Keyword.id == MealKeywordReview.keyword_id
    ).filter(
        MealKeywordReview.meal_id == meal_id
    ).group_by(
        Keyword.id, Keyword.name
    ).order_by(
        desc('count')
    ).limit(top_n).all()
    
    keywords = [
        MealKeywordStats(keyword_id=kw_id, keyword_name=kw_name, count=count)
        for kw_id, kw_name, count in stats
    ]
    
    return MealKeywordStatsResponse(meal_id=meal_id, keywords=keywords)


def get_user_keyword_reviews(
    db: Session,
    meal_id: int,
    user_id: str
) -> List[MealKeywordReview]:
    """사용자가 특정 메뉴에 남긴 키워드 리뷰 조회"""
    return db.query(MealKeywordReview).filter(
        MealKeywordReview.meal_id == meal_id,
        MealKeywordReview.user_id == user_id
    ).all()

