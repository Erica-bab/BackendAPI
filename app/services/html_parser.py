from bs4 import BeautifulSoup
import re
from typing import Dict, List


class HTMLParser:
    """HTML 파싱 서비스"""
    
    def parse_meal_html(self, html: str) -> Dict:
        """
        한양대 급식 HTML을 파싱하여 구조화된 데이터로 변환
        
        Args:
            html: 한양대 급식 페이지 HTML
            
        Returns:
            파싱된 급식 정보 딕셔너리
        """
        soup = BeautifulSoup(html, "html.parser")
        
        # 식당 이름 파싱
        restaurant_name = self._parse_restaurant_name(soup)
        
        # 날짜와 요일 파싱
        date, day_of_week = self._parse_date_info(soup)
        
        # 급식 메뉴 파싱
        meals = self._parse_meals(soup)
        
        return {
            "restaurant": restaurant_name,
            "date": date,
            "day_of_week": day_of_week,
            **meals
        }
    
    def _parse_restaurant_name(self, soup: BeautifulSoup) -> str:
        """식당 이름 파싱"""
        restaurant_tag = soup.find("strong", class_="font-point5")
        if restaurant_tag:
            return restaurant_tag.get_text(strip=True)
        return ""
    
    def _parse_date_info(self, soup: BeautifulSoup) -> tuple:
        """날짜와 요일 파싱"""
        date = ""
        day_of_week = ""
        
        day_selc = soup.find("div", class_="day-selc")
        if day_selc:
            date_tag = day_selc.find("strong")
            if date_tag:
                date = date_tag.get_text(strip=True)
            
            # strong 태그 바로 다음 span 태그가 요일
            spans = day_selc.find_all("span")
            for span in spans:
                if span.get_text(strip=True) and not span.get("class"):
                    day_of_week = span.get_text(strip=True)
                    break
        
        return date, day_of_week
    
    def _get_current_day_of_week(self, soup: BeautifulSoup) -> str:
        """현재 요일 가져오기"""
        day_selc = soup.find("div", class_="day-selc")
        if day_selc:
            spans = day_selc.find_all("span")
            for span in spans:
                text = span.get_text(strip=True)
                if text in ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]:
                    return text
        return ""
    
    def _parse_meals(self, soup: BeautifulSoup) -> Dict[str, List[Dict]]:
        """급식 메뉴 파싱 (h4 d-title2 클래스 기반)"""
        meals = {"조식": [], "중식": [], "석식": []}
        
        # h4 태그에서 d-title2 클래스를 가진 요소들 찾기
        h4_elements = soup.find_all("h4", class_="d-title2")
        
        for h4 in h4_elements:
            text = h4.get_text(strip=True)
            
            # 식사 종류 확인
            meal_type = None
            if "조식" in text:
                meal_type = "조식"
            elif "중식" in text:
                meal_type = "중식"
            elif "석식" in text:
                meal_type = "석식"
            
            if not meal_type:
                continue
            
            # h4 다음에 오는 메뉴 정보 찾기
            menu_items = self._find_menu_items_after_h4(h4)
            
            for menu_data in menu_items:
                if menu_data.get("menu_text"):
                    # 메뉴 파싱
                    meal_item = self._parse_menu_item(menu_data, meal_type)
                    if meal_item:
                        meals[meal_type].append(meal_item)
        
        # 각 식사 종류별로 중복 제거
        for meal_type in ["조식", "중식", "석식"]:
            meals[meal_type] = self._remove_duplicate_meals(meals[meal_type])
        
        return meals
    
    def _remove_duplicate_meals(self, meal_list: List[Dict]) -> List[Dict]:
        """메뉴 리스트에서 중복 제거 (korean_name 기준)"""
        seen = set()
        unique_meals = []
        
        for meal in meal_list:
            # korean_name을 문자열로 변환하여 중복 체크
            korean_key = str(meal.get("korean", []))
            if korean_key not in seen:
                seen.add(korean_key)
                unique_meals.append(meal)
        
        return unique_meals
    
    def _find_menu_items_after_h4(self, h4_element) -> List[Dict]:
        """h4 요소 다음에 오는 메뉴 아이템들 찾기"""
        menu_items = []
        
        # h4의 부모 요소에서 div.bbs 찾기
        parent = h4_element.parent
        if not parent:
            return menu_items
        
        # div.bbs 찾기
        bbs_divs = parent.find_all("div", class_="bbs")
        
        for bbs_div in bbs_divs:
            # ul.thumbnails > li.span3 구조 찾기
            ul_thumbnails = bbs_div.find_all("ul", class_="thumbnails")
            
            for ul in ul_thumbnails:
                li_span3_elements = ul.find_all("li", class_="span3")
                
                for li in li_span3_elements:
                    # h3 태그에서 메뉴 텍스트 가져오기
                    h3_tag = li.find("h3")
                    menu_text = h3_tag.get_text(strip=True) if h3_tag else ""
                    
                    # p.price 태그에서 가격 가져오기
                    price_tag = li.find("p", class_="price")
                    price_text = price_tag.get_text(strip=True) if price_tag else ""
                    
                    # img 태그에서 이미지 URL 가져오기
                    img_tag = li.find("img")
                    image_url = img_tag.get("src", "") if img_tag else ""
                    if image_url.startswith("/"):
                        image_url = "https://www.hanyang.ac.kr" + image_url
                    
                    if menu_text:
                        menu_items.append({
                            "menu_text": menu_text,
                            "price": price_text,
                            "image_url": image_url
                        })
        
        return menu_items
    
    def _parse_menu_item(self, menu_data: Dict, meal_type: str) -> Dict:
        """메뉴 아이템 파싱"""
        menu_text = menu_data.get("menu_text", "")
        if not menu_text or menu_text == "-":
            return None
        
        # 메뉴 유효성 검사 (안내 문구 필터링)
        if self._is_notice_text(menu_text):
            return None
        
        # 태그 추출 (대괄호 안의 텍스트)
        tags = self._extract_tags(menu_text)
        
        # 태그를 제거한 메뉴 리스트
        korean_name_list = self._split_to_list(menu_text)
        
        # 메뉴 리스트 유효성 검사
        if not self._is_valid_menu_list(korean_name_list):
            return None
        
        return {
            "korean": korean_name_list,
            "tags": tags,
            "price": menu_data.get("price", ""),
            "image": menu_data.get("image_url", ""),
            "meal_type": meal_type
        }
    
    def _parse_table_menu_item(self, menu_text: str, meal_type: str) -> Dict:
        """테이블에서 메뉴 아이템 파싱"""
        if not menu_text or menu_text == "-":
            return None
        
        # 메뉴 유효성 검사 (안내 문구 필터링)
        if self._is_notice_text(menu_text):
            return None
        
        # 태그 추출 (대괄호 안의 텍스트)
        tags = self._extract_tags(menu_text)
        
        # 태그를 제거한 메뉴 리스트
        korean_name_list = self._split_to_list(menu_text)
        
        # 메뉴 리스트 유효성 검사
        if not self._is_valid_menu_list(korean_name_list):
            return None
        
        return {
            "korean": korean_name_list,
            "tags": tags,
            "price": "",  # 테이블 구조에서는 가격 정보가 없음
            "image": "",  # 테이블 구조에서는 이미지 정보가 없음
            "meal_type": meal_type
        }
    
    def _is_notice_text(self, text: str) -> bool:
        """안내 문구인지 확인"""
        # 더 정확한 안내 문구 패턴 매칭
        notice_patterns = [
            r"운영합니다",
            r"코너만.*운영",
            r"금요일.*한.*코너만",
            r"휴무|휴업",
            r"문의.*전화",
            r"연락.*안내",
            r"공지.*알림"
        ]
        
        import re
        for pattern in notice_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # 단순 키워드 매칭 (더 엄격하게)
        simple_keywords = ["운영합니다", "휴무", "휴업", "문의", "전화", "연락", "안내", "공지", "알림"]
        text_lower = text.lower()
        for keyword in simple_keywords:
            if keyword in text_lower:
                return True
        
        return False
    
    def _is_valid_menu_list(self, menu_list: List[str]) -> bool:
        """메뉴 리스트가 유효한지 확인"""
        if not menu_list:
            return False
        
        # 너무 짧은 단어들만 있는 경우 필터링
        valid_items = [item for item in menu_list if len(item) >= 2]
        if len(valid_items) < len(menu_list) * 0.5:  # 50% 이상이 유효해야 함
            return False
        
        # 안내 문구 키워드가 포함된 경우 필터링
        for item in menu_list:
            if self._is_notice_text(item):
                return False
        
        return True
    
    def _parse_meal_item(self, item) -> Dict:
        """개별 메뉴 아이템 파싱"""
        h3 = item.find("h3")
        price_tag = item.find("p", class_="price")
        img = item.find("img")
        
        if not h3:
            return None
        
        # <br> 기준으로 분리해서 첫 번째는 한국어, 두 번째는 영어
        parts = h3.get_text("\n", strip=True).split("\n")
        korean_text = parts[0].strip()
        
        # 태그 추출 (대괄호 안의 텍스트)
        tags = self._extract_tags(korean_text)
        
        # 태그를 제거한 메뉴 리스트
        korean_name_list = self._split_to_list(korean_text)
        
        # 가격
        price = price_tag.get_text(strip=True) if price_tag else ""
        
        # 이미지 URL (절대경로 변환)
        img_url = img["src"] if img and "src" in img.attrs else ""
        if img_url.startswith("/"):
            img_url = "https://www.hanyang.ac.kr" + img_url
        
        return {
            "korean": korean_name_list,
            "tags": tags,
            "price": price,
            "image": img_url
        }
    
    def _extract_tags(self, text: str) -> List[str]:
        """
        대괄호 안의 텍스트를 태그로 추출
        예: "[중식A]스팸마요덮밥" -> ["중식A"]
        """
        if not text:
            return []
        
        # 대괄호 안의 모든 텍스트 추출
        tags = re.findall(r'\[([^\]]+)\]', text)
        return tags
    
    def _split_to_list(self, text: str) -> List[str]:
        """
        텍스트를 적절한 구분자로 분리하여 리스트로 변환
        식당마다 다른 구분자를 사용할 수 있으므로 여러 패턴을 시도
        대괄호 안의 텍스트는 제거됨
        """
        if not text:
            return []
        
        # 대괄호 제거 (태그는 별도로 처리됨)
        text_without_tags = re.sub(r'\[[^\]]+\]', '', text)
        
        # 특별한 경우: 안내 문구는 그대로 반환
        if any(keyword in text_without_tags for keyword in ["운영 없습니다", "추석연휴", "휴무", "휴업"]):
            return [text_without_tags.strip()]
        
        # 1순위: 탭 문자로 분리 시도
        if '\t' in text_without_tags:
            items = re.split(r'\s*\t\s*', text_without_tags)
            result = [item.strip() for item in items if item.strip()]
            if result:
                return result
        
        # 2순위: 개행 문자로 분리 시도
        if '\n' in text_without_tags:
            items = text_without_tags.split('\n')
            result = [item.strip() for item in items if item.strip()]
            if result and len(result) > 1:
                return result
        
        # 3순위: / 로 분리 시도 (일부 식당에서 사용)
        if '/' in text_without_tags and text_without_tags.count('/') >= 2:
            items = text_without_tags.split('/')
            result = [item.strip() for item in items if item.strip()]
            if result and len(result) > 1:
                return result
        
        # 4순위: 연속된 공백 2개 이상으로 분리 시도
        items = re.split(r'\s{2,}', text_without_tags)
        result = [item.strip() for item in items if item.strip()]
        if result and len(result) > 1:
            return result
        
        # 5순위: 특정 패턴으로 분리 (예: "요구르트참치김치찌개" -> "요구르트", "참치김치찌개")
        # 한글 단어 경계를 찾아서 분리
        korean_words = re.findall(r'[가-힣]+', text_without_tags)
        if len(korean_words) > 1:
            # 단어가 2개 이상이면 분리
            return korean_words
        
        # 6순위: 단일 공백으로 분리 (모든 식당에서 리스트로 만들기)
        # 각 단어를 개별 아이템으로 분리
        items = text_without_tags.split()
        result = [item.strip() for item in items if item.strip()]
        if result:
            return result
        
        # 분리할 수 없으면 전체를 하나의 아이템으로 반환
        return [text_without_tags.strip()] if text_without_tags.strip() else []

