from typing import List, Dict, Any, Optional

class Memory:
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        self.kv_store: Dict[str, Any] = {}

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def get_messages(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        if limit is not None:
            return self.messages[-limit:]
        return self.messages[:]

    def set(self, key: str, value: Any):
        self.kv_store[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.kv_store.get(key, default) 