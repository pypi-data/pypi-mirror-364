import requests
from typing import Any
from ..session import Session
from ..provider import BaseProvider

class GenericProvider(BaseProvider):
    def __init__(self, api_url: str):
        self.api_url = api_url

    def generate(self, prompt: str, session: Session, **kwargs) -> Any:
        data = {"prompt": prompt}
        data.update(kwargs)
        response = requests.post(
            self.api_url,
            json=data,
            cookies=session.as_dict()
        )
        response.raise_for_status()
        return response.json() 