from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.rating import (
    RatingCreate, RatingResponse, RatingUpdate, MealRatingStats
)
from app.crud import rating as crud_rating, meal as crud_meal

router = APIRouter()


@router.post("/", response_model=RatingResponse, summary="평점 등록/수정")
async def create_or_update_rating(
    rating_data: RatingCreate,
    db: Session = Depends(get_db)
):
    """
    메뉴에 평점을 등록하거나 수정합니다.
    
    - 같은 사용자가 같은 메뉴에 이미 평점을 남긴 경우 수정됩니다.
    - **오픈시간 제한**: 당일 해당 식사 종류의 오픈시간에만 작성 가능
    - **meal_id**: 메뉴 ID
    - **user_id**: 사용자 ID
    - **rating**: 평점 (1.0 ~ 5.0)
    
    ### 오픈시간:
    - **조식**: 07:40 ~ 09:00
    - **중식**: 11:30 ~ 13:30
    - **석식**: 17:30 ~ 19:00
    """
    # 메뉴 존재 확인
    meal = crud_meal.get_meal_by_id(db, rating_data.meal_id)
    if not meal:
        raise HTTPException(status_code=404, detail="메뉴를 찾을 수 없습니다.")
    
    # 오픈시간 체크
    from app.utils.meal_time_checker import check_review_permission
    permission = check_review_permission(meal.meal_type, meal.date)
    
    if not permission["allowed"]:
        raise HTTPException(
            status_code=403, 
            detail=f"리뷰 작성 불가: {permission['reason']} (오픈시간: {permission['open_time']}, 현재: {permission['current_time']})"
        )
    
    try:
        rating = crud_rating.create_or_update_rating(db, rating_data)
        return rating
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"평점 등록 실패: {str(e)}")


@router.get("/meal/{meal_id}", response_model=MealRatingStats, summary="메뉴 평점 통계 조회")
async def get_meal_rating_stats(
    meal_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 메뉴의 평점 통계를 조회합니다.
    
    - **meal_id**: 메뉴 ID
    
    반환값:
    - 평균 평점
    - 평점 개수
    - 평점 분포 (1점~5점별 개수)
    """
    # 메뉴 존재 확인
    meal = crud_meal.get_meal_by_id(db, meal_id)
    if not meal:
        raise HTTPException(status_code=404, detail="메뉴를 찾을 수 없습니다.")
    
    stats = crud_rating.get_meal_rating_stats(db, meal_id)
    return stats


@router.get("/meal/{meal_id}/user/{user_id}", response_model=RatingResponse, summary="사용자의 메뉴 평점 조회")
async def get_user_rating(
    meal_id: int,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    특정 사용자가 특정 메뉴에 남긴 평점을 조회합니다.
    """
    rating = crud_rating.get_user_rating(db, meal_id, user_id)
    if not rating:
        raise HTTPException(status_code=404, detail="평점을 찾을 수 없습니다.")
    return rating


@router.delete("/meal/{meal_id}/user/{user_id}", summary="평점 삭제")
async def delete_rating(
    meal_id: int,
    user_id: str,
    db: Session = Depends(get_db)
):
    """평점을 삭제합니다."""
    success = crud_rating.delete_rating(db, meal_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="평점을 찾을 수 없습니다.")
    return {"message": "평점이 삭제되었습니다."}

