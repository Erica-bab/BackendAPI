#!/usr/bin/env python3
"""
10월 5일 창의인재원식당 정확한 정보 확인
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.meal_service import meal_service
from bs4 import BeautifulSoup

def check_correct_info():
    """10월 5일 창의인재원식당 정확한 정보 확인"""
    print("=== 10월 5일 창의인재원식당 정확한 정보 확인 ===\n")
    
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
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        # 테이블 찾기
        tables = soup.find_all("table", class_="tables-board")
        menu_table = None
        
        for table in tables:
            rows = table.find_all("tr")
            if len(rows) >= 3:
                first_row = rows[0]
                cells = first_row.find_all(["td", "th"])
                if len(cells) >= 7:  # 월~토요일
                    menu_table = table
                    break
        
        if menu_table:
            rows = menu_table.find_all("tr")
            
            # 각 행 분석
            for row_idx, row in enumerate(rows):
                cells = row.find_all(["td", "th"])
                if len(cells) < 2:
                    continue
                
                # 첫 번째 셀에서 식사 종류 확인
                meal_type_cell = cells[0]
                meal_type_text = meal_type_cell.get_text(strip=True)
                
                if meal_type_text in ["조식", "중식", "석식"]:
                    print(f"\n=== {meal_type_text} ===")
                    
                    # 모든 셀 확인 (일요일 관련 정보 찾기)
                    for cell_idx, cell in enumerate(cells):
                        text = cell.get_text(strip=True)
                        if text and ("일요일" in text or "추석연휴" in text or "운영 없습니다" in text):
                            print(f"셀 {cell_idx}: {repr(text)}")
                            print(f"HTML: {cell}")
                            
                            # ul 태그 확인
                            ul_tag = cell.find("ul", class_="bs-ul")
                            if ul_tag:
                                li_tags = ul_tag.find_all("li")
                                for li_idx, li in enumerate(li_tags):
                                    li_text = li.get_text(strip=True)
                                    print(f"  li {li_idx+1}: {repr(li_text)}")
        
        # 특정 키워드로 전체 검색
        print("\n=== 키워드 전체 검색 ===")
        keywords = ["일요일", "추석연휴", "운영 없습니다"]
        for keyword in keywords:
            elements = soup.find_all(string=lambda text: text and keyword in text)
            print(f"'{keyword}' 포함 요소: {len(elements)}개")
            for elem in elements[:5]:  # 처음 5개만
                parent = elem.parent
                print(f"  - {parent.name}: {repr(elem.strip())}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_correct_info()
