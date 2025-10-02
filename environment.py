from typing import Any

class Environment:
    def __init__(self) -> None:
        self.stack = []
        self.variables: dict[str, Any] = {}
