from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from datetime import date, datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from app.schemas.meal import MealResponse, RestaurantsResponse, RestaurantInfo, MealInDB
from app.services.meal_service import meal_service
from app.services.meal_fetcher import meal_fetcher
from app.db.session import get_db
from app.crud import meal as crud_meal
from app.core.config import settings
from app.api.dependencies import AdminAuth

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


@router.get("/available-dates", summary="저장된 급식 날짜 조회")
async def get_available_dates(
    restaurant_code: Optional[str] = Query(None, description="식당 코드 (선택사항)"),
    db: Session = Depends(get_db)
):
    """
    DB에 저장된 급식 날짜 목록을 조회합니다.
    
    - restaurant_code: 특정 식당의 날짜만 조회 (선택사항)
    - 모든 식당의 날짜를 조회하려면 restaurant_code 생략
    """
    dates = crud_meal.get_available_dates(db, restaurant_code)
    return {
        "restaurant_code": restaurant_code,
        "available_dates": dates,
        "total_count": len(dates)
    }


@router.get("/parse/{restaurant_code}", summary="웹에서 급식 정보 직접 파싱")
async def parse_meal_from_web(
    restaurant_code: str,
    year: int = Query(..., description="년도"),
    month: int = Query(..., description="월"),
    day: int = Query(..., description="일"),
    db: Session = Depends(get_db)
):
    """
    한양대 웹사이트에서 직접 급식 정보를 파싱하여 반환합니다.
    DB에 저장하지 않고 실시간으로 파싱합니다.
    
    - restaurant_code: 식당 코드 (re11, re12, re13, re15)
    - year, month, day: 조회할 날짜
    """
    # 식당 코드 유효성 검사
    restaurant = crud_meal.get_restaurant_by_code(db, restaurant_code)
    if not restaurant:
        raise HTTPException(status_code=404, detail="잘못된 식당 코드입니다.")
    
    try:
        # 웹에서 직접 파싱
        from app.services.meal_service import meal_service
        from app.services.html_parser import HTMLParser
        
        html_parser = HTMLParser()
        
        # 한양대 서버에서 HTML 가져오기
        html_content = meal_service.get_meal_html(restaurant_code, year, month, day)
        
        if not html_content:
            raise HTTPException(status_code=404, detail="급식 정보를 찾을 수 없습니다.")
        
        # HTML 파싱
        parsed_data = html_parser.parse_meal_html(html_content)
        
        # 응답 형식으로 변환
        response_data = {
            "restaurant": restaurant.name,
            "date": parsed_data.get("date", f"{year}. {month:02d}. {day:02d}"),
            "day_of_week": parsed_data.get("day_of_week", ""),
            "조식": [],
            "중식": [],
            "석식": []
        }
        
        # 각 식사별로 메뉴 정리 (새로운 파싱 로직에 맞게 수정)
        for meal_type in ["조식", "중식", "석식"]:
            meals = parsed_data.get(meal_type, [])
            for meal in meals:
                # 메뉴 아이템 변환
                menu_item = {
                    "korean_name": meal.get("korean", []),
                    "tags": meal.get("tags", []),
                    "price": meal.get("price", ""),
                    "image_url": meal.get("image", ""),
                    "source": "web_parsing"  # 파싱 소스 표시
                }
                response_data[meal_type].append(menu_item)
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"급식 정보 파싱 중 오류가 발생했습니다: {str(e)}")


@router.post("/fetch", summary="급식 정보 수집 (관리자용)")
async def fetch_meals(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    api_key: str = AdminAuth
):
    """
    급식 정보를 수동으로 수집합니다. (관리자용)
    
    현재 날짜부터 설정된 기간(기본 14일)의 급식 정보를 한양대 서버에서 가져와 DB에 저장합니다.
    백그라운드에서 실행되므로 즉시 응답을 받습니다.
    
    **인증 필요**: X-API-Key 헤더에 관리자 API 키를 포함해야 합니다.
    """
    background_tasks.add_task(meal_fetcher.fetch_and_store_meals, db)
    return {
        "message": "급식 정보 수집이 백그라운드에서 시작되었습니다.",
        "days_ahead": settings.MEAL_FETCH_DAYS_AHEAD
    }

