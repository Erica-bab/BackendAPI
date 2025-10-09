from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from datetime import date, datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from app.schemas.meal import (
    RestaurantDetailInfo, MealInDB, FlexibleMealResponse, RestaurantMeals,
    RestaurantsDetailResponse
)
from app.services.meal_service import meal_service
from app.services.meal_fetcher import meal_fetcher
from app.db.session import get_db
from app.crud import meal as crud_meal
from app.core.config import settings
from app.api.dependencies import AdminAuth

router = APIRouter()


@router.get("/", response_model=FlexibleMealResponse, summary="급식 정보 조회")
async def get_meals_flexible(
    year: Optional[int] = Query(None, description="연도 (기본값: 오늘)"),
    month: Optional[int] = Query(None, ge=1, le=12, description="월 (1-12, 기본값: 오늘)"),
    day: Optional[int] = Query(None, ge=1, le=31, description="일 (1-31, 기본값: 오늘)"),
    restaurant_codes: Optional[str] = Query(None, description="식당 코드 (콤마로 구분, 예: re11,re12,re13)"),
    meal_types: Optional[str] = Query(None, description="식사 종류 (콤마로 구분, 예: 조식,중식,석식 또는 1,2,3)"),
    db: Session = Depends(get_db)
):
    """
    급식 정보를 유연하게 조회합니다.
    
    ### 사용 예시:
    - **날짜만**: 모든 식당의 모든 시간대 급식 반환
    - **날짜 + 식당코드**: 선택한 식당들의 모든 시간대 급식 반환
    - **날짜 + 시간대**: 모든 식당의 선택한 시간대 급식만 반환
    - **날짜 + 시간대 + 식당코드**: 선택한 식당의 선택한 시간대 급식만 반환
    
    ### 파라미터:
    - **year, month, day**: 조회할 날짜 (생략시 오늘 날짜)
    - **restaurant_codes**: 식당 코드 (콤마로 구분, 예: re11,re12,re13) - 여러 개 선택 가능
    - **meal_types**: 식사 종류 (콤마로 구분, 예: 조식,중식,석식 또는 1,2,3) - 여러 개 선택 가능
    
    ### 식당 코드:
    - **re11**: 교직원식당
    - **re12**: 학생식당
    - **re13**: 창의인재원식당
    - **re15**: 창업보육센터
    
    ### 식사 종류:
    - **조식** 또는 **1**: 조식
    - **중식** 또는 **2**: 중식
    - **석식** 또는 **3**: 석식
    
    ### 예제:
    - `/api/v1/meals` - 오늘의 모든 식당, 모든 시간대
    - `/api/v1/meals?restaurant_codes=re11,re12` - 오늘의 교직원식당과 학생식당
    - `/api/v1/meals?meal_types=중식,석식` - 오늘의 모든 식당의 중식과 석식만
    - `/api/v1/meals?meal_types=2,3` - 오늘의 모든 식당의 중식과 석식만 (숫자 사용)
    - `/api/v1/meals?restaurant_codes=re11&meal_types=중식` - 오늘의 교직원식당 중식만
    - `/api/v1/meals?restaurant_codes=re11&meal_types=2` - 오늘의 교직원식당 중식만 (숫자 사용)
    """
    # 날짜가 지정되지 않은 경우 오늘 날짜 사용
    today = datetime.now()
    year = year or today.year
    month = month or today.month
    day = day or today.day
    
    try:
        target_date = date(year, month, day)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"잘못된 날짜입니다: {str(e)}")
    
    # 콤마로 구분된 문자열을 리스트로 변환
    restaurant_codes_list = None
    if restaurant_codes:
        restaurant_codes_list = [code.strip() for code in restaurant_codes.split(",") if code.strip()]
    
    meal_types_list = None
    if meal_types:
        # 숫자와 한글 매핑
        meal_type_mapping = {
            "1": "조식",
            "2": "중식",
            "3": "석식",
            "조식": "조식",
            "중식": "중식",
            "석식": "석식"
        }
        
        raw_types = [mt.strip() for mt in meal_types.split(",") if mt.strip()]
        meal_types_list = []
        
        for mt in raw_types:
            if mt in meal_type_mapping:
                meal_types_list.append(meal_type_mapping[mt])
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"잘못된 식사 종류입니다: '{mt}'. 사용 가능한 종류: 조식(1), 중식(2), 석식(3)"
                )
    
    # 식당 코드 검증
    if restaurant_codes_list:
        invalid_codes = [code for code in restaurant_codes_list if code not in settings.RESTAURANT_CODES]
        if invalid_codes:
            raise HTTPException(
                status_code=400, 
                detail=f"잘못된 식당 코드입니다: {invalid_codes}. 사용 가능한 코드: {list(settings.RESTAURANT_CODES.keys())}"
            )
    
    try:
        # DB에서 급식 정보 조회
        meals = crud_meal.get_meals_flexible(db, target_date, restaurant_codes_list, meal_types_list)
        
        # 식당별로 그룹화
        from collections import defaultdict
        restaurants_data = defaultdict(lambda: {"조식": [], "중식": [], "석식": []})
        restaurant_info = {}  # 식당 정보 저장
        day_of_week = ""
        
        for meal in meals:
            restaurant = meal.restaurant
            restaurant_code = restaurant.code
            restaurant_name = restaurant.name
            
            # 식당 정보 저장
            if restaurant_code not in restaurant_info:
                restaurant_info[restaurant_code] = restaurant_name
            
            # 요일 정보 (첫 번째 메뉴에서 가져옴)
            if not day_of_week and meal.day_of_week:
                day_of_week = meal.day_of_week
            
            # 식사 종류별로 분류
            restaurants_data[restaurant_code][meal.meal_type].append(meal)
        
        # 응답 데이터 구성
        restaurants_list = []
        
        # restaurant_codes_list가 지정된 경우 해당 순서대로, 아니면 설정 순서대로
        codes_to_use = restaurant_codes_list if restaurant_codes_list else list(settings.RESTAURANT_CODES.keys())
        
        for code in codes_to_use:
            # 데이터가 있는 식당만 포함
            if code in restaurants_data or code in restaurant_info:
                restaurant_meals = RestaurantMeals(
                    restaurant_code=code,
                    restaurant_name=restaurant_info.get(code, settings.RESTAURANT_CODES.get(code, code)),
                    조식=restaurants_data[code]["조식"],
                    중식=restaurants_data[code]["중식"],
                    석식=restaurants_data[code]["석식"]
                )
                restaurants_list.append(restaurant_meals)
        
        # 데이터가 전혀 없는 경우에도 요청한 식당 정보는 포함 (빈 리스트로)
        if not restaurants_list and restaurant_codes_list:
            for code in restaurant_codes_list:
                restaurants_list.append(RestaurantMeals(
                    restaurant_code=code,
                    restaurant_name=settings.RESTAURANT_CODES.get(code, code),
                    조식=[],
                    중식=[],
                    석식=[]
                ))
        
        return FlexibleMealResponse(
            date=target_date.strftime("%Y. %m. %d"),
            day_of_week=day_of_week,
            restaurants=restaurants_list
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@router.get("/restaurants", response_model=RestaurantsDetailResponse, summary="식당 정보 조회")
async def get_restaurants(
    restaurant_codes: Optional[str] = Query(None, description="식당 코드 (콤마로 구분, 예: re11,re12,re13)")
):
    """
    식당 정보를 조회합니다. (위치 및 운영시간 포함)
    
    ### 사용 예시:
    - **파라미터 없음**: 모든 식당의 상세 정보 반환
    - **restaurant_codes 지정**: 선택한 식당들의 상세 정보만 반환
    
    ### 파라미터:
    - **restaurant_codes**: 식당 코드 (콤마로 구분, 예: re11,re12) - 선택사항
    
    ### 식당 코드:
    - **re11**: 교직원식당
    - **re12**: 학생식당
    - **re13**: 창의인재원식당
    - **re15**: 창업보육센터
    
    ### 예제:
    - `/api/v1/meals/restaurants` - 모든 식당 정보
    - `/api/v1/meals/restaurants?restaurant_codes=re11` - 교직원식당만
    - `/api/v1/meals/restaurants?restaurant_codes=re11,re12` - 교직원식당과 학생식당
    """
    # 콤마로 구분된 문자열을 리스트로 변환
    restaurant_codes_list = None
    if restaurant_codes:
        restaurant_codes_list = [code.strip() for code in restaurant_codes.split(",") if code.strip()]
        
        # 식당 코드 검증
        invalid_codes = [code for code in restaurant_codes_list if code not in settings.RESTAURANT_CODES]
        if invalid_codes:
            raise HTTPException(
                status_code=400,
                detail=f"잘못된 식당 코드입니다: {invalid_codes}. 사용 가능한 코드: {list(settings.RESTAURANT_CODES.keys())}"
            )
    
    # 조회할 식당 코드 결정 (지정되지 않으면 모든 식당)
    codes_to_fetch = restaurant_codes_list if restaurant_codes_list else list(settings.RESTAURANT_CODES.keys())
    
    # 각 식당의 상세 정보 수집
    restaurants_list = []
    for code in codes_to_fetch:
        restaurant_name = settings.RESTAURANT_CODES[code]
        location_info = settings.RESTAURANT_LOCATIONS.get(code, {})
        open_times = settings.RESTAURANT_OPEN_TIMES.get(code, {})
        
        restaurant_detail = RestaurantDetailInfo(
            code=code,
            name=restaurant_name,
            address=location_info.get("address"),
            building=location_info.get("building"),
            floor=location_info.get("floor"),
            latitude=location_info.get("latitude"),
            longitude=location_info.get("longitude"),
            description=location_info.get("description"),
            open_times=open_times
        )
        restaurants_list.append(restaurant_detail)
    
    return RestaurantsDetailResponse(restaurants=restaurants_list)


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

