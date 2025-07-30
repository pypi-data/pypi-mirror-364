from typing import Dict

class Session:
    def __init__(self, cookies: Dict[str, str] = None):
        self.cookies = cookies or {}

    def set_cookie(self, key: str, value: str):
        self.cookies[key] = value

    def get_cookie(self, key: str):
        return self.cookies.get(key)

    def as_dict(self):
        return self.cookies 