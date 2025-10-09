from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import date as date_type


class MealItemBase(BaseModel):
    """메뉴 아이템 기본"""
    korean_name: List[str] = Field(..., description="한국어 메뉴명 리스트")
    tags: List[str] = Field(default=[], description="태그 리스트 (예: [중식A], [특식])")
    price: str = Field(..., description="가격")
    image_url: str = Field(..., description="이미지 URL")


class MealItem(MealItemBase):
    """개별 메뉴 아이템 (API 응답용 - DB 저장 전)"""
    korean: List[str] = Field(..., description="한국어 메뉴명 리스트 (호환성)")
    image: str = Field(..., description="이미지 URL (호환성)")
    
    @classmethod
    def from_base(cls, base: MealItemBase):
        return cls(
            korean_name=base.korean_name,
            tags=base.tags,
            price=base.price,
            image_url=base.image_url,
            korean=base.korean_name,
            image=base.image_url
        )


class MealInDB(MealItemBase):
    """DB에 저장되는 메뉴"""
    id: int
    restaurant_id: int
    date: date_type
    day_of_week: str
    meal_type: str
    
    # 평점 정보 추가
    average_rating: Optional[float] = Field(None, description="평균 평점")
    rating_count: int = Field(default=0, description="평점 개수")
    
    class Config:
        from_attributes = True


class MealResponse(BaseModel):
    """급식 정보 응답"""
    restaurant: str = Field(..., description="식당 이름")
    date: str = Field(..., description="날짜")
    day_of_week: str = Field(..., description="요일")
    breakfast: List[MealInDB] = Field(default=[], description="조식", alias="조식")
    lunch: List[MealInDB] = Field(default=[], description="중식", alias="중식")
    dinner: List[MealInDB] = Field(default=[], description="석식", alias="석식")
    
    class Config:
        populate_by_name = True


class RestaurantInfo_Detail(BaseModel):
    """식당 정보"""
    code: str = Field(..., description="식당 코드")
    name: str = Field(..., description="식당 이름")
    address: Optional[str] = Field(None, description="주소")
    building: Optional[str] = Field(None, description="건물명")
    floor: Optional[str] = Field(None, description="층수")
    latitude: Optional[str] = Field(None, description="위도")
    longitude: Optional[str] = Field(None, description="경도")
    description: Optional[str] = Field(None, description="위치 설명")
    open_times: Optional[Dict[str, Optional[str]]] = Field(None, description="운영시간 정보")
    
    
class RestaurantInfo(BaseModel):
    """식당 정보"""
    code: str = Field(..., description="식당 코드")
    name: str = Field(..., description="식당 이름")


class RestaurantDetailInfo(RestaurantInfo_Detail):
    """식당 상세 정보 (위치 정보 포함)"""
    pass


class RestaurantsResponse(BaseModel):
    """식당 목록 응답"""
    restaurants: List[RestaurantInfo]


class RestaurantsDetailResponse(BaseModel):
    """식당 상세 정보 응답"""
    restaurants: List[RestaurantDetailInfo]


class RestaurantMeals(BaseModel):
    """식당별 급식 정보"""
    restaurant_code: str = Field(..., description="식당 코드")
    restaurant_name: str = Field(..., description="식당 이름")
    breakfast: List[MealInDB] = Field(default=[], description="조식", alias="조식")
    lunch: List[MealInDB] = Field(default=[], description="중식", alias="중식")
    dinner: List[MealInDB] = Field(default=[], description="석식", alias="석식")
    
    class Config:
        populate_by_name = True


class FlexibleMealResponse(BaseModel):
    """유연한 급식 조회 응답"""
    date: str = Field(..., description="날짜")
    day_of_week: str = Field(default="", description="요일")
    restaurants: List[RestaurantMeals] = Field(..., description="식당별 급식 정보")

