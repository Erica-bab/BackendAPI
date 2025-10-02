import ssl
import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

class SSLContextAdapter(HTTPAdapter):
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().proxy_manager_for(*args, **kwargs)


# SSLContext 만들기 (보안레벨 낮춤)
ctx = ssl.create_default_context()
ctx.set_ciphers("DEFAULT@SECLEVEL=1")

session = requests.Session()
session.mount("https://", SSLContextAdapter(ctx))

restaurant_code = "re11"
day, year, month = 2, 2025, 10
api_url = f"https://www.hanyang.ac.kr/web/www/{restaurant_code}?p_p_id=foodView_WAR_foodportlet&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_pos=1&p_p_col_count=2&_foodView_WAR_foodportlet_sFoodDateDay={day}&_foodView_WAR_foodportlet_sFoodDateYear={year}&_foodView_WAR_foodportlet_action=view&_foodView_WAR_foodportlet_sFoodDateMonth={month-1}"

response = session.get(api_url, headers={"User-Agent": "Mozilla/5.0"})
print(response.status_code)
print(response.text[:500])
