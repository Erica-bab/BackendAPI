import requests
from typing import Dict
from datetime import date

from app.core.config import settings
from app.utils.ssl_adapter import create_ssl_session
from app.services.html_parser import HTMLParser


class MealService:
    """급식 정보 조회 서비스"""
    
    def __init__(self):
        self.session = create_ssl_session()
        self.parser = HTMLParser()
    
    def get_meal_info(
        self, 
        restaurant_code: str, 
        year: int, 
        month: int, 
        day: int
    ) -> Dict:
        """
        급식 정보 조회
        
        Args:
            restaurant_code: 식당 코드 (re11, re12, re13, re15)
            year: 연도
            month: 월 (1-12)
            day: 일 (1-31)
            
        Returns:
            파싱된 급식 정보
            
        Raises:
            ValueError: 잘못된 파라미터
            requests.exceptions.RequestException: 요청 실패
        """
        # 입력값 검증
        self._validate_params(restaurant_code, year, month, day)
        
        # HTML 가져오기
        html = self._fetch_html(restaurant_code, year, month, day)
        
        # 파싱
        meal_data = self.parser.parse_meal_html(html)
        
        return meal_data
    
    def _validate_params(
        self, 
        restaurant_code: str, 
        year: int, 
        month: int, 
        day: int
    ):
        """파라미터 유효성 검증"""
        if restaurant_code not in settings.RESTAURANT_CODES:
            raise ValueError(
                f"잘못된 식당 코드입니다. 사용 가능한 코드: {list(settings.RESTAURANT_CODES.keys())}"
            )
        
        if not (1 <= day <= 31):
            raise ValueError("day는 1~31 사이의 값이어야 합니다.")
        
        if not (1 <= month <= 12):
            raise ValueError("month는 1~12 사이의 값이어야 합니다.")
        
        if year <= 0:
            raise ValueError("year는 0보다 큰 값이어야 합니다.")
    
    def _fetch_html(
        self, 
        restaurant_code: str, 
        year: int, 
        month: int, 
        day: int
    ) -> str:
        """한양대 서버에서 HTML 가져오기"""
        api_url = (
            f"{settings.HANYANG_BASE_URL}/web/www/{restaurant_code}"
            f"?p_p_id=foodView_WAR_foodportlet"
            f"&p_p_lifecycle=0"
            f"&p_p_state=normal"
            f"&p_p_mode=view"
            f"&p_p_col_id=column-1"
            f"&p_p_col_pos=1"
            f"&p_p_col_count=2"
            f"&_foodView_WAR_foodportlet_sFoodDateDay={day}"
            f"&_foodView_WAR_foodportlet_sFoodDateYear={year}"
            f"&_foodView_WAR_foodportlet_action=view"
            f"&_foodView_WAR_foodportlet_sFoodDateMonth={month - 1}"
        )
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        try:
            response = self.session.get(api_url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"한양대 서버 요청 실패: {e}")
    
    def get_meal_html(
        self, 
        restaurant_code: str, 
        year: int, 
        month: int, 
        day: int
    ) -> str:
        """
        한양대 서버에서 HTML 가져오기 (외부 호출용)
        
        Args:
            restaurant_code: 식당 코드 (re11, re12, re13, re15)
            year: 연도
            month: 월 (1-12)
            day: 일 (1-31)
            
        Returns:
            HTML 문자열
            
        Raises:
            ValueError: 잘못된 파라미터
            requests.exceptions.RequestException: 요청 실패
        """
        # 입력값 검증
        self._validate_params(restaurant_code, year, month, day)
        
        # HTML 가져오기
        return self._fetch_html(restaurant_code, year, month, day)
    
    def get_available_restaurants(self) -> Dict[str, str]:
        """사용 가능한 식당 목록 반환"""
        return settings.RESTAURANT_CODES


# 싱글톤 인스턴스
meal_service = MealService()

