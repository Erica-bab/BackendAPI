#!/usr/bin/env python3
"""
10월 5일 창의인재원식당 수정된 파서 테스트
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.meal_service import meal_service
from app.services.html_parser import HTMLParser

def test_fixed_parser():
    """10월 5일 창의인재원식당 수정된 파서 테스트"""
    print("=== 10월 5일 창의인재원식당 수정된 파서 테스트 ===\n")
    
    restaurant_code = "re13"
    year = 2025
    month = 10
    day = 5
    
    try:
        html_content = meal_service.get_meal_html(
            restaurant_code, 
            year, 
            month, 
            day
        )
        
        html_parser = HTMLParser()
        parsed_data = html_parser.parse_meal_html(html_content)
        
        print(f"식당명: {parsed_data.get('restaurant', 'N/A')}")
        print(f"날짜: {parsed_data.get('date', 'N/A')}")
        print(f"요일: {parsed_data.get('day_of_week', 'N/A')}")
        print()
        
        # 각 식사별 메뉴 출력
        total_menus = 0
        for meal_type in ["조식", "중식", "석식"]:
            meals = parsed_data.get(meal_type, [])
            total_menus += len(meals)
            print(f"{meal_type}: {len(meals)}개 메뉴")
            
            for i, meal in enumerate(meals, 1):
                korean_menu = meal.get('korean', [])
                tags = meal.get('tags', [])
                print(f"  {i}. {korean_menu}")
                if tags:
                    print(f"     태그: {tags}")
        
        print(f"\n총 메뉴: {total_menus}개")
        
        # 예상 결과와 비교
        print("\n=== 예상 결과와 비교 ===")
        print("예상:")
        print("  조식: ['일요일', '조식', '운영', '없습니다']")
        print("  중식: ['추석연휴']")
        print("  석식: ['추석연휴']")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_parser()
