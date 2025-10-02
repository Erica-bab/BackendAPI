from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import Optional
from app.models.rating import Rating
from app.schemas.rating import RatingCreate, RatingUpdate, MealRatingStats


def create_or_update_rating(
    db: Session,
    rating_data: RatingCreate
) -> Rating:
    """평점 생성 또는 수정"""
    existing_rating = db.query(Rating).filter(
        Rating.meal_id == rating_data.meal_id,
        Rating.user_id == rating_data.user_id
    ).first()
    
    if existing_rating:
        # 기존 평점 수정
        existing_rating.rating = rating_data.rating
        db.commit()
        db.refresh(existing_rating)
        return existing_rating
    else:
        # 새 평점 생성
        new_rating = Rating(
            meal_id=rating_data.meal_id,
            user_id=rating_data.user_id,
            rating=rating_data.rating
        )
        db.add(new_rating)
        db.commit()
        db.refresh(new_rating)
        return new_rating


def get_user_rating(
    db: Session,
    meal_id: int,
    user_id: str
) -> Optional[Rating]:
    """사용자의 특정 메뉴 평점 조회"""
    return db.query(Rating).filter(
        Rating.meal_id == meal_id,
        Rating.user_id == user_id
    ).first()


def get_meal_rating_stats(
    db: Session,
    meal_id: int
) -> MealRatingStats:
    """메뉴 평점 통계"""
    # 평균 평점과 개수
    stats = db.query(
        func.avg(Rating.rating).label('average'),
        func.count(Rating.id).label('count')
    ).filter(Rating.meal_id == meal_id).first()
    
    # 평점 분포
    distribution = db.query(
        func.floor(Rating.rating).label('rating'),
        func.count(Rating.id).label('count')
    ).filter(Rating.meal_id == meal_id).group_by(
        func.floor(Rating.rating)
    ).all()
    
    rating_dist = {int(rating): count for rating, count in distribution}
    
    return MealRatingStats(
        meal_id=meal_id,
        average_rating=round(stats.average, 2) if stats.average else 0.0,
        rating_count=stats.count or 0,
        rating_distribution=rating_dist
    )


def delete_rating(
    db: Session,
    meal_id: int,
    user_id: str
) -> bool:
    """평점 삭제"""
    rating = db.query(Rating).filter(
        Rating.meal_id == meal_id,
        Rating.user_id == user_id
    ).first()
    
    if rating:
        db.delete(rating)
        db.commit()
        return True
    return False

