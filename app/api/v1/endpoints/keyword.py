from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.keyword import (
    KeywordCreate, KeywordResponse, KeywordReviewCreate,
    KeywordReviewResponse, MealKeywordStatsResponse
)
from app.crud import keyword as crud_keyword, meal as crud_meal

router = APIRouter()


@router.get("/", response_model=List[KeywordResponse], summary="키워드 목록 조회")
async def get_keywords(
    category: str = Query(None, description="카테고리 필터 (긍정/부정)"),
    db: Session = Depends(get_db)
):
    """
    키워드 목록을 조회합니다.
    - category: 긍정/부정으로 필터링 (선택사항)
    """
    if category:
        keywords = crud_keyword.get_keywords_by_category(db, category)
    else:
        keywords = crud_keyword.get_all_keywords(db)
    return keywords


@router.post("/", response_model=KeywordResponse, summary="키워드 생성 (관리자용)")
async def create_keyword(
    keyword_data: KeywordCreate,
    db: Session = Depends(get_db)
):
    """
    새로운 키워드를 생성합니다. (관리자용)
    
    - **name**: 키워드 이름
    - **category**: 키워드 카테고리 (선택)
    - **display_order**: 표시 순서 (기본값: 0)
    """
    try:
        keyword = crud_keyword.create_keyword(db, keyword_data)
        return keyword
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"키워드 생성 실패: {str(e)}")


@router.post("/review", response_model=KeywordReviewResponse, summary="키워드 리뷰 등록")
async def create_keyword_review(
    review_data: KeywordReviewCreate,
    db: Session = Depends(get_db)
):
    """
    메뉴에 키워드 리뷰를 등록합니다.
    
    - **meal_id**: 메뉴 ID
    - **keyword_id**: 키워드 ID
    - **user_id**: 사용자 ID
    
    같은 사용자가 같은 메뉴에 같은 키워드를 중복으로 선택할 수 없습니다.
    """
    # 메뉴 존재 확인
    meal = crud_meal.get_meal_by_id(db, review_data.meal_id)
    if not meal:
        raise HTTPException(status_code=404, detail="메뉴를 찾을 수 없습니다.")
    
    # 키워드 존재 확인
    keyword = crud_keyword.get_keyword_by_id(db, review_data.keyword_id)
    if not keyword:
        raise HTTPException(status_code=404, detail="키워드를 찾을 수 없습니다.")
    
    try:
        review = crud_keyword.create_keyword_review(db, review_data)
        # 응답에 키워드 이름 추가
        response = KeywordReviewResponse(
            id=review.id,
            meal_id=review.meal_id,
            keyword_id=review.keyword_id,
            keyword_name=keyword.name,
            user_id=review.user_id,
            created_at=review.created_at
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"키워드 리뷰 등록 실패: {str(e)}")


@router.delete("/review/meal/{meal_id}/keyword/{keyword_id}/user/{user_id}", summary="키워드 리뷰 삭제")
async def delete_keyword_review(
    meal_id: int,
    keyword_id: int,
    user_id: str,
    db: Session = Depends(get_db)
):
    """키워드 리뷰를 삭제합니다."""
    success = crud_keyword.delete_keyword_review(db, meal_id, keyword_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="키워드 리뷰를 찾을 수 없습니다.")
    return {"message": "키워드 리뷰가 삭제되었습니다."}


@router.get("/stats/meal/{meal_id}", response_model=MealKeywordStatsResponse, summary="메뉴 키워드 통계 조회")
async def get_meal_keyword_stats(
    meal_id: int,
    top_n: int = Query(default=10, ge=1, le=50, description="상위 N개 키워드"),
    db: Session = Depends(get_db)
):
    """
    특정 메뉴의 키워드 통계를 조회합니다.
    
    - **meal_id**: 메뉴 ID
    - **top_n**: 상위 N개 키워드 (기본값: 10)
    
    반환값: 선택된 횟수가 많은 순서대로 키워드 목록
    """
    # 메뉴 존재 확인
    meal = crud_meal.get_meal_by_id(db, meal_id)
    if not meal:
        raise HTTPException(status_code=404, detail="메뉴를 찾을 수 없습니다.")
    
    stats = crud_keyword.get_meal_keyword_stats(db, meal_id, top_n)
    return stats


@router.get("/review/meal/{meal_id}/user/{user_id}", response_model=List[KeywordReviewResponse], summary="사용자의 키워드 리뷰 조회")
async def get_user_keyword_reviews(
    meal_id: int,
    user_id: str,
    db: Session = Depends(get_db)
):
    """특정 사용자가 특정 메뉴에 남긴 키워드 리뷰를 조회합니다."""
    reviews = crud_keyword.get_user_keyword_reviews(db, meal_id, user_id)
    
    # 키워드 이름 포함하여 응답
    result = []
    for review in reviews:
        keyword = crud_keyword.get_keyword_by_id(db, review.keyword_id)
        result.append(KeywordReviewResponse(
            id=review.id,
            meal_id=review.meal_id,
            keyword_id=review.keyword_id,
            keyword_name=keyword.name if keyword else "",
            user_id=review.user_id,
            created_at=review.created_at
        ))
    
    return result

