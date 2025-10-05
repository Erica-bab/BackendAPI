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

