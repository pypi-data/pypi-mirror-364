from typing import Any
from .session import Session

class BaseProvider:
    def generate(self, prompt: str, session: Session, **kwargs) -> Any:
        raise NotImplementedError("Provider must implement generate method.") 

class GenericProvider:
    def __init__(self, api_url, headers=None, body_template=None, auto_token_headers=False):
        self.api_url = api_url
        self.headers = headers or {}
        self.body_template = body_template
        self.auto_token_headers = auto_token_headers

    def _inject_token_headers(self, session, headers):
        # Extract tokens from session cookies and set as headers if present
        cookies = getattr(session, 'cookies', {})
        auth_token = cookies.get("__Secure-next-auth.session-token")
        conduit_token = cookies.get("x-conduit-token")
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        if conduit_token:
            headers["x-conduit-token"] = conduit_token
        return headers

    def __call__(self, prompt, session=None, *args, **kwargs):
        import requests
        body = self.body_template(prompt) if self.body_template else {"prompt": prompt}
        headers = dict(self.headers)
        if self.auto_token_headers and session is not None:
            headers = self._inject_token_headers(session, headers)
        response = requests.post(self.api_url, json=body, headers=headers, cookies=getattr(session, 'cookies', {}))
        try:
            return response.json()
        except Exception:
            return response.text 