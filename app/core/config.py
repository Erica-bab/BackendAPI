from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # API 설정
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "한양대 ERICA 급식 API"
    VERSION: str = "2.0.0"
    DESCRIPTION: str = "한양대학교 ERICA 식당 메뉴 조회 및 평점/리뷰 API"
    
    # CORS 설정
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # 한양대 API 설정
    HANYANG_BASE_URL: str = "https://www.hanyang.ac.kr"
    
    # 식당 코드 매핑
    RESTAURANT_CODES: dict = {
        "re11": "교직원식당",
        "re12": "학생식당",
        "re13": "창의인재원식당",
        "re15": "창업보육센터"
    }
    
    # 식당 위치 정보
    RESTAURANT_LOCATIONS: dict = {
        "re11": {
            "address": "경기도 안산시 상록구 한양대학로 55",
            "building": "학생회관",
            "floor": "3층",
            "latitude": "37.298047",
            "longitude": "126.834415",
            "description": "학생회관 3층에 위치한 교직원 식당입니다."
        },
        "re12": {
            "address": "경기도 안산시 상록구 한양대학로 55",
            "building": "학생회관",
            "floor": "2층",
            "latitude": "37.298047",
            "longitude": "126.834415",
            "description": "학생회관 2층에 위치한 학생 식당입니다."
        },
        "re13": {
            "address": "경기도 안산시 상록구 한양대학로 55",
            "building": "창의인재원",
            "floor": "1층",
            "latitude": "37.291276",
            "longitude": "126.836354",
            "description": "창의인재원 1층에 위치한 식당입니다."
        },
        "re15": {
            "address": "경기도 안산시 상록구 한양대학로 55",
            "building": "창업보육센터",
            "floor": "지하 1층",
            "latitude": "37.295626",
            "longitude": "126.837253",
            "description": "창업보육센터 지하 1층에 위치한 식당입니다."
        }
    }
    
    RESTAURANT_OPEN_TIMES: dict = {
        "re11": {
            "Breakfast": None,
            "Lunch": "11:30 ~ 13:30",
            "Dinner": None
            },
        "re12": {
            "Breakfast": None,
            "Lunch": "11:30 ~ 13:30",
            "Dinner": None
            },
        "re13": {
            "Breakfast": "07:40 ~ 09:00",
            "Lunch": "11:30 ~ 13:20",
            "Dinner": "17:30 ~ 19:00"
            },
        "re15": {
            "Breakfast": None,
            "Lunch": "11:30 ~ 13:30",
            "Dinner": "17:00 ~ 18:30"
            },
    }
    
    # 데이터베이스 설정
    DATABASE_URL: str = "mysql+pymysql://user:password@localhost:3306/meal_db?charset=utf8mb4"
    
    # 급식 데이터 수집 설정
    MEAL_FETCH_DAYS_AHEAD: int = 14  # 현재부터 2주치 데이터 수집
    MEAL_FETCH_SCHEDULE: str = "0 2 * * *"  # 매일 새벽 2시에 실행 (cron 표현식)
    
    # 관리자 API 키 설정
    ADMIN_API_KEY: str = "admin_meal_api_2025"  # 패치 API용 인증 키
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()

