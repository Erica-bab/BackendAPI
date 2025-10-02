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
    
    def _parse_meals(self, soup: BeautifulSoup) -> Dict[str, List[Dict]]:
        """급식 메뉴 파싱"""
        meals = {"조식": [], "중식": [], "석식": []}
        sections = soup.find_all("div", class_="in-box")
        
        for section in sections:
            title_tag = section.find("h4", class_="d-title2")
            if not title_tag:
                continue
            
            meal_type = title_tag.get_text(strip=True)
            items = section.find_all("li", class_="span3")
            
            for item in items:
                meal_item = self._parse_meal_item(item)
                if meal_item:
                    meals[meal_type].append(meal_item)
        
        return meals
    
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
        
        # 5순위: 단일 공백으로 분리 (모든 식당에서 리스트로 만들기)
        # 각 단어를 개별 아이템으로 분리
        items = text_without_tags.split()
        result = [item.strip() for item in items if item.strip()]
        if result:
            return result
        
        # 분리할 수 없으면 전체를 하나의 아이템으로 반환
        return [text_without_tags.strip()] if text_without_tags.strip() else []

