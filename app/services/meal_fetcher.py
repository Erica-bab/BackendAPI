from datetime import date, timedelta
from sqlalchemy.orm import Session
from typing import Dict
import logging

from app.services.meal_service import MealService
from app.core.config import settings
from app.crud import meal as crud_meal

logger = logging.getLogger(__name__)


class MealFetcher:
    """급식 정보 수집 서비스"""
    
    def __init__(self):
        self.meal_service = MealService()
    
    def fetch_and_store_meals(self, db: Session):
        """
        모든 식당의 급식 정보를 가져와서 DB에 저장
        (현재 날짜부터 MEAL_FETCH_DAYS_AHEAD일 후까지)
        """
        today = date.today()
        end_date = today + timedelta(days=settings.MEAL_FETCH_DAYS_AHEAD)
        
        logger.info(f"급식 정보 수집 시작: {today} ~ {end_date}")
        
        total_saved = 0
        
        for restaurant_code, restaurant_name in settings.RESTAURANT_CODES.items():
            try:
                # 식당 정보 가져오기 또는 생성
                restaurant = crud_meal.get_or_create_restaurant(
                    db, restaurant_code, restaurant_name
                )
                
                # 날짜별로 데이터 수집
                current_date = today
                while current_date <= end_date:
                    try:
                        count = self._fetch_and_store_single_day(
                            db, restaurant, restaurant_code, current_date
                        )
                        total_saved += count
                    except Exception as e:
                        logger.error(
                            f"급식 정보 수집 실패 - {restaurant_name} {current_date}: {e}"
                        )
                    
                    current_date += timedelta(days=1)
                
                logger.info(f"{restaurant_name} 급식 정보 수집 완료")
                
            except Exception as e:
                logger.error(f"{restaurant_name} 급식 정보 수집 중 오류: {e}")
        
        logger.info(f"급식 정보 수집 완료. 총 {total_saved}개 메뉴 저장")
        return total_saved
    
    def _fetch_and_store_single_day(
        self,
        db: Session,
        restaurant,
        restaurant_code: str,
        target_date: date
    ) -> int:
        """특정 날짜의 급식 정보 수집 및 저장"""
        # 한양대 서버에서 데이터 가져오기
        meal_data = self.meal_service.get_meal_info(
            restaurant_code,
            target_date.year,
            target_date.month,
            target_date.day
        )
        
        saved_count = 0
        
        # 각 식사 종류별로 저장
        for meal_type in ["조식", "중식", "석식"]:
            meals = meal_data.get(meal_type, [])
            
            for meal_item in meals:
                try:
                    # 중복 체크를 위한 메뉴명 문자열 생성
                    korean_name_str = str(meal_item["korean"]) if isinstance(meal_item["korean"], list) else meal_item["korean"]
                    
                    # 중복 체크 (같은 날짜, 같은 메뉴명)
                    existing = db.query(crud_meal.Meal).filter(
                        crud_meal.Meal.restaurant_id == restaurant.id,
                        crud_meal.Meal.date == target_date,
                        crud_meal.Meal.meal_type == meal_type
                    ).first()
                    
                    # 리스트로 변환되었는지 확인하고 기존과 동일한지 체크
                    if existing:
                        existing_korean = existing.korean_name if isinstance(existing.korean_name, list) else [existing.korean_name]
                        new_korean = meal_item["korean"] if isinstance(meal_item["korean"], list) else [meal_item["korean"]]
                        if existing_korean == new_korean:
                            continue
                    
                    if not existing:
                        # 새로운 메뉴 생성
                        crud_meal.create_meal(
                            db=db,
                            restaurant_id=restaurant.id,
                            date=target_date,
                            day_of_week=meal_data.get("day_of_week", ""),
                            meal_type=meal_type,
                            korean_name=meal_item["korean"],
                            tags=meal_item.get("tags", []),
                            price=meal_item.get("price", ""),
                            image_url=meal_item.get("image", "")
                        )
                        saved_count += 1
                
                except Exception as e:
                    logger.error(f"메뉴 저장 실패: {e}")
        
        return saved_count


meal_fetcher = MealFetcher()

