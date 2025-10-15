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


@router.get("/", summary="급식 정보 조회")
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
        
        # 응답에 포함할 식사 종류 결정 (지정되지 않으면 모든 종류)
        meal_types_to_include = meal_types_list if meal_types_list else ["조식", "중식", "석식"]
        
        # restaurant_codes_list가 지정된 경우 해당 순서대로, 아니면 설정 순서대로
        codes_to_use = restaurant_codes_list if restaurant_codes_list else list(settings.RESTAURANT_CODES.keys())
        
        for code in codes_to_use:
            # 데이터가 있는 식당만 포함
            if code in restaurants_data or code in restaurant_info:
                # 식당 기본 정보
                restaurant_meal_data = {
                    "restaurant_code": code,
                    "restaurant_name": restaurant_info.get(code, settings.RESTAURANT_CODES.get(code, code))
                }
                
                # 선택한 식사 종류만 추가
                for meal_type in meal_types_to_include:
                    restaurant_meal_data[meal_type] = restaurants_data[code][meal_type]
                
                restaurants_list.append(restaurant_meal_data)
        
        # 데이터가 전혀 없는 경우에도 요청한 식당 정보는 포함 (빈 리스트로)
        if not restaurants_list and restaurant_codes_list:
            for code in restaurant_codes_list:
                restaurant_meal_data = {
                    "restaurant_code": code,
                    "restaurant_name": settings.RESTAURANT_CODES.get(code, code)
                }
                # 선택한 식사 종류만 빈 리스트로 추가
                for meal_type in meal_types_to_include:
                    restaurant_meal_data[meal_type] = []
                restaurants_list.append(restaurant_meal_data)
        
        return {
            "date": target_date.strftime("%Y. %m. %d"),
            "day_of_week": day_of_week,
            "restaurants": restaurants_list
        }
        
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


# @router.get("/open-times", summary="식사 종류별 오픈시간 조회")
# async def get_meal_open_times():
#     """
#     식사 종류별 오픈시간을 조회합니다.
    
#     리뷰 작성 가능한 시간대를 확인할 수 있습니다.
#     """
#     from app.utils.meal_time_checker import MEAL_OPEN_TIMES, get_meal_open_time_string
    
#     result = {}
#     for meal_type in ["조식", "중식", "석식"]:
#         result[meal_type] = {
#             "open_time": get_meal_open_time_string(meal_type),
#             "start_time": MEAL_OPEN_TIMES[meal_type]["start"].strftime("%H:%M"),
#             "end_time": MEAL_OPEN_TIMES[meal_type]["end"].strftime("%H:%M")
#         }
    
#     return {
#         "message": "식사 종류별 오픈시간",
#         "open_times": result,
#         "note": "리뷰는 당일 해당 식사 종류의 오픈시간에만 작성 가능합니다."
#     }


@router.post("/remove-duplicates", summary="중복 급식 데이터 제거 (관리자용)")
async def remove_duplicate_meals(
    db: Session = Depends(get_db),
    api_key: str = AdminAuth
):
    """
    중복된 급식 데이터를 제거합니다. (관리자용)
    
    동일한 restaurant_id, date, meal_type, korean_name을 가진 중복 데이터를 찾아서
    가장 최신에 생성된 것만 남기고 나머지는 삭제합니다.
    
    **인증 필요**: X-API-Key 헤더에 관리자 API 키를 포함해야 합니다.
    
    **응답**:
    - total_meals_before: 중복 제거 전 총 급식 데이터 수
    - deleted_count: 삭제된 중복 데이터 수
    - total_meals_after: 중복 제거 후 총 급식 데이터 수
    """
    from app.models.meal import Meal
    
    try:
        # 중복 제거 전 데이터 개수
        total_before = db.query(Meal).count()
        
        # 중복 데이터 찾기 및 제거
        all_meals = db.query(Meal).order_by(Meal.restaurant_id, Meal.date, Meal.meal_type).all()
        
        seen = {}
        duplicates_to_delete = []
        
        for meal in all_meals:
            # 고유 키 생성
            key = (
                meal.restaurant_id,
                meal.date,
                meal.meal_type,
                str(meal.korean_name)  # JSON을 문자열로 변환
            )
            
            if key in seen:
                # 중복 발견 - 이전 것을 삭제 대상으로 표시
                duplicates_to_delete.append(seen[key])
                # 현재 것을 최신으로 갱신
                seen[key] = meal
            else:
                # 처음 본 조합
                seen[key] = meal
        
        # 중복 데이터 삭제
        deleted_count = 0
        for meal_to_delete in duplicates_to_delete:
            db.delete(meal_to_delete)
            deleted_count += 1
        
        db.commit()
        
        # 중복 제거 후 데이터 개수
        total_after = db.query(Meal).count()
        
        return {
            "message": "중복 급식 데이터 제거 완료",
            "total_meals_before": total_before,
            "deleted_count": deleted_count,
            "total_meals_after": total_after
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"중복 제거 중 오류 발생: {str(e)}")

