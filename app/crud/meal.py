from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import date

from app.models.meal import Meal
from app.models.restaurant import Restaurant
from app.models.rating import Rating


def get_restaurant_by_code(db: Session, code: str) -> Optional[Restaurant]:
    """식당 코드로 식당 조회"""
    return db.query(Restaurant).filter(Restaurant.code == code).first()


def create_restaurant(db: Session, code: str, name: str) -> Restaurant:
    """식당 생성"""
    restaurant = Restaurant(code=code, name=name)
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant


def get_or_create_restaurant(db: Session, code: str, name: str) -> Restaurant:
    """식당 가져오기 또는 생성"""
    restaurant = get_restaurant_by_code(db, code)
    if not restaurant:
        restaurant = create_restaurant(db, code, name)
    return restaurant


def create_meal(
    db: Session,
    restaurant_id: int,
    date: date,
    day_of_week: str,
    meal_type: str,
    korean_name,  # List[str] 또는 리스트
    tags,  # List[str] 또는 리스트
    price: str,
    image_url: str
) -> Meal:
    """메뉴 생성"""
    meal = Meal(
        restaurant_id=restaurant_id,
        date=date,
        day_of_week=day_of_week,
        meal_type=meal_type,
        korean_name=korean_name,
        tags=tags,
        price=price,
        image_url=image_url
    )
    db.add(meal)
    db.commit()
    db.refresh(meal)
    return meal


def get_meals_by_date(
    db: Session, 
    restaurant_code: str, 
    target_date: date
) -> List[Meal]:
    """특정 날짜의 급식 메뉴 조회 (평점 정보 포함)"""
    meals = db.query(
        Meal,
        func.avg(Rating.rating).label('average_rating'),
        func.count(Rating.id).label('rating_count')
    ).join(
        Restaurant, Meal.restaurant_id == Restaurant.id
    ).outerjoin(
        Rating, Meal.id == Rating.meal_id
    ).filter(
        and_(
            Restaurant.code == restaurant_code,
            Meal.date == target_date
        )
    ).group_by(Meal.id).all()
    
    # 평점 정보를 Meal 객체에 동적으로 추가
    result = []
    for meal, avg_rating, rating_count in meals:
        meal.average_rating = round(avg_rating, 2) if avg_rating else None
        meal.rating_count = rating_count or 0
        result.append(meal)
    
    return result


def get_meal_by_id(db: Session, meal_id: int) -> Optional[Meal]:
    """메뉴 ID로 조회"""
    return db.query(Meal).filter(Meal.id == meal_id).first()


def get_available_dates(db: Session, restaurant_code: Optional[str] = None) -> List[str]:
    """저장된 급식 날짜 목록 조회"""
    from sqlalchemy import distinct, func
    
    query = db.query(distinct(Meal.date))
    
    if restaurant_code:
        # 특정 식당의 날짜만 조회
        restaurant = get_restaurant_by_code(db, restaurant_code)
        if restaurant:
            query = query.filter(Meal.restaurant_id == restaurant.id)
        else:
            return []
    
    # 날짜 순으로 정렬
    dates = query.order_by(Meal.date).all()
    
    # 날짜를 문자열로 변환 (YYYY-MM-DD 형식)
    return [str(date[0]) for date in dates]


def delete_meals_by_date_range(
    db: Session,
    restaurant_id: int,
    start_date: date,
    end_date: date
):
    """특정 기간의 메뉴 삭제"""
    db.query(Meal).filter(
        and_(
            Meal.restaurant_id == restaurant_id,
            Meal.date >= start_date,
            Meal.date <= end_date
        )
    ).delete()
    db.commit()

