import ssl
from requests.adapters import HTTPAdapter


class SSLContextAdapter(HTTPAdapter):
    """SSL 보안 레벨을 낮춰서 한양대 서버에 접속하기 위한 어댑터"""
    
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().proxy_manager_for(*args, **kwargs)


def create_ssl_session():
    """SSL 세션 생성"""
    import requests
    
    ctx = ssl.create_default_context()
    ctx.set_ciphers("DEFAULT@SECLEVEL=1")
    
    session = requests.Session()
    session.mount("https://", SSLContextAdapter(ctx))
    
    return session

