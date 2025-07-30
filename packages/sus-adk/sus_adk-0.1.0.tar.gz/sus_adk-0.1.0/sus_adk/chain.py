from typing import List, Any, Callable

class Chain:
    def __init__(self, steps: List[Callable[[Any], Any]]):
        self.steps = steps

    def run(self, input_data: Any) -> Any:
        data = input_data
        for step in self.steps:
            data = step(data)
        return data 