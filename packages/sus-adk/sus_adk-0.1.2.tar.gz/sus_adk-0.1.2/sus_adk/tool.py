from typing import Callable, Any, Dict, Optional

class Tool:
    def __init__(self, name: str, description: str, func: Callable[..., Any], arg_schema: Optional[Dict[str, type]] = None):
        self.name = name
        self.description = description
        self.func = func
        self.arg_schema = arg_schema or {}

    def validate_args(self, **kwargs):
        for arg, arg_type in self.arg_schema.items():
            if arg not in kwargs:
                raise ValueError(f"Missing required argument: {arg}")
            if not isinstance(kwargs[arg], arg_type):
                raise TypeError(f"Argument '{arg}' must be of type {arg_type.__name__}")

    def run(self, *args, **kwargs) -> Any:
        if self.arg_schema:
            self.validate_args(**kwargs)
        return self.func(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)

    def openai_function_spec(self):
        """
        Return a dict compatible with OpenAI function-calling API.
        """
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        for arg, arg_type in self.arg_schema.items():
            parameters["properties"][arg] = {"type": self._type_to_openai(arg_type)}
            parameters["required"].append(arg)
        return {
            "name": self.name,
            "description": self.description,
            "parameters": parameters
        }

    @staticmethod
    def _type_to_openai(py_type):
        if py_type is int:
            return "integer"
        if py_type is float:
            return "number"
        if py_type is bool:
            return "boolean"
        return "string" 