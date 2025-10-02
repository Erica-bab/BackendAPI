from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from datetime import date, datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.schemas.meal import MealResponse, RestaurantsResponse, RestaurantInfo, MealInDB
from app.services.meal_service import meal_service
from app.services.meal_fetcher import meal_fetcher
from app.db.session import get_db
from app.crud import meal as crud_meal
from app.core.config import settings

router = APIRouter()


@router.get("/restaurants", response_model=RestaurantsResponse, summary="식당 목록 조회")
async def get_restaurants():
    """
    사용 가능한 식당 목록을 조회합니다.
    """
    restaurants_data = settings.RESTAURANT_CODES
    restaurants = [
        RestaurantInfo(code=code, name=name)
        for code, name in restaurants_data.items()
    ]
    return RestaurantsResponse(restaurants=restaurants)


@router.get("/{restaurant_code}", response_model=MealResponse, summary="급식 정보 조회 (DB)")
async def get_meal(
    restaurant_code: str,
    year: Optional[int] = Query(None, description="연도 (기본값: 오늘)"),
    month: Optional[int] = Query(None, ge=1, le=12, description="월 (1-12, 기본값: 오늘)"),
    day: Optional[int] = Query(None, ge=1, le=31, description="일 (1-31, 기본값: 오늘)"),
    db: Session = Depends(get_db)
):
    """
    특정 식당의 급식 정보를 DB에서 조회합니다.
    
    - **restaurant_code**: 식당 코드 (re11: 교직원식당, re12: 학생식당, re13: 창의인재원식당, re15: 창업보육센터)
    - **year**: 조회할 연도 (생략시 오늘)
    - **month**: 조회할 월 (생략시 오늘)
    - **day**: 조회할 일 (생략시 오늘)
    """
    # 날짜가 지정되지 않은 경우 오늘 날짜 사용
    today = datetime.now()
    year = year or today.year
    month = month or today.month
    day = day or today.day
    target_date = date(year, month, day)
    
    # 식당 코드 확인
    if restaurant_code not in settings.RESTAURANT_CODES:
        raise HTTPException(status_code=400, detail="잘못된 식당 코드입니다.")
    
    try:
        # DB에서 급식 정보 조회
        meals = crud_meal.get_meals_by_date(db, restaurant_code, target_date)
        
        # 식당 정보
        restaurant = crud_meal.get_restaurant_by_code(db, restaurant_code)
        restaurant_name = restaurant.name if restaurant else settings.RESTAURANT_CODES[restaurant_code]
        
        # 응답 데이터 구성
        meal_data = {
            "restaurant": restaurant_name,
            "date": target_date.strftime("%Y. %m. %d"),
            "day_of_week": meals[0].day_of_week if meals else "",
            "조식": [],
            "중식": [],
            "석식": []
        }
        
        for meal in meals:
            meal_data[meal.meal_type].append(meal)
        
        return meal_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@router.get("/{restaurant_code}/today", response_model=MealResponse, summary="오늘의 급식 정보 조회")
async def get_today_meal(
    restaurant_code: str,
    db: Session = Depends(get_db)
):
    """
    특정 식당의 오늘 급식 정보를 조회합니다.
    
    - **restaurant_code**: 식당 코드 (re11: 교직원식당, re12: 학생식당, re13: 창의인재원식당, re15: 창업보육센터)
    """
    today = datetime.now()
    return await get_meal(restaurant_code, today.year, today.month, today.day, db)


@router.post("/fetch", summary="급식 정보 수집 (관리자용)")
async def fetch_meals(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    급식 정보를 수동으로 수집합니다. (관리자용)
    
    현재 날짜부터 설정된 기간(기본 14일)의 급식 정보를 한양대 서버에서 가져와 DB에 저장합니다.
    백그라운드에서 실행되므로 즉시 응답을 받습니다.
    """
    background_tasks.add_task(meal_fetcher.fetch_and_store_meals, db)
    return {
        "message": "급식 정보 수집이 백그라운드에서 시작되었습니다.",
        "days_ahead": settings.MEAL_FETCH_DAYS_AHEAD
    }

