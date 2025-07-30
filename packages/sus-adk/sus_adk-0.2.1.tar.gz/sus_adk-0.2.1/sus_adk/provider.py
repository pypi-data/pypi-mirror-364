from typing import Any
from .session import Session

class BaseProvider:
    def generate(self, prompt: str, session: Session, **kwargs) -> Any:
        raise NotImplementedError("Provider must implement generate method.") 