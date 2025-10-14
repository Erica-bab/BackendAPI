from datetime import date, timedelta
from sqlalchemy.orm import Session
from typing import Dict
import logging
import threading
import time

from app.services.meal_service import MealService
from app.core.config import settings
from app.crud import meal as crud_meal

logger = logging.getLogger(__name__)

# 급식 수집 작업 락 (동시 실행 방지)
_meal_fetch_lock = threading.Lock()


class MealFetcher:
    """급식 정보 수집 서비스"""
    
    def __init__(self):
        self.meal_service = MealService()
    
    def fetch_and_store_meals(self, db: Session):
        """
        모든 식당의 급식 정보를 가져와서 DB에 저장
        (현재 날짜부터 MEAL_FETCH_DAYS_AHEAD일 후까지)
        """
        # 동시 실행 방지를 위한 락 체크
        if not _meal_fetch_lock.acquire(blocking=False):
            logger.warning("급식 정보 수집이 이미 진행 중입니다. 현재 요청을 건너뜁니다.")
            return 0
        
        try:
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
            
        finally:
            # 락 해제
            _meal_fetch_lock.release()
            logger.info("급식 정보 수집 락 해제")
    
    def _fetch_and_store_single_day(
        self,
        db: Session,
        restaurant,
        restaurant_code: str,
        target_date: date
    ) -> int:
        """특정 날짜의 급식 정보 수집 및 저장"""
        # 한양대 서버에서 HTML 가져오기
        html_content = self.meal_service.get_meal_html(
            restaurant_code,
            target_date.year,
            target_date.month,
            target_date.day
        )
        
        # HTML 파싱
        from app.services.html_parser import HTMLParser
        html_parser = HTMLParser()
        meal_data = html_parser.parse_meal_html(html_content)
        
        saved_count = 0
        
        # 각 식사 종류별로 저장
        for meal_type in ["조식", "중식", "석식"]:
            meals = meal_data.get(meal_type, [])
            
            if meals:  # 해당 식사 종류에 메뉴가 있는 경우만 처리
                try:
                    # 1. 해당 날짜/식당/식사종류의 기존 메뉴 모두 삭제
                    from app.models.meal import Meal
                    existing_meals = db.query(Meal).filter(
                        Meal.restaurant_id == restaurant.id,
                        Meal.date == target_date,
                        Meal.meal_type == meal_type
                    ).all()
                    
                    if existing_meals:
                        logger.info(f"기존 메뉴 삭제: {restaurant.name} {target_date} {meal_type} ({len(existing_meals)}개)")
                        for old_meal in existing_meals:
                            db.delete(old_meal)
                        db.commit()
                    
                    # 2. 새로운 메뉴들 저장
                    for meal_item in meals:
                        try:
                            new_korean = meal_item["korean"] if isinstance(meal_item["korean"], list) else [meal_item["korean"]]
                            
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
                            logger.info(f"새 메뉴 저장: {restaurant.name} {target_date} {meal_type} - {new_korean}")
                            
                        except Exception as meal_error:
                            logger.error(f"개별 메뉴 저장 실패: {e}")
                            logger.error(f"메뉴 데이터: {meal_item}")
                            import traceback
                            logger.error(f"상세 오류: {traceback.format_exc()}")
                            
                except Exception as meal_type_error:
                    logger.error(f"{meal_type} 저장 실패: {meal_type_error}")
                    import traceback
                    logger.error(f"상세 오류: {traceback.format_exc()}")
        
        return saved_count


meal_fetcher = MealFetcher()

